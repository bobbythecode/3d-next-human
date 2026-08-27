"""Apply macros on a headless MakeHuman Human and export OBJ metres Y-up."""

from __future__ import annotations

import threading
from typing import Any

import numpy as np

from .bootstrap import ensure_runtime, qt_imported
from .body_measures import apply_body_cm
from .catalog import ALIAS_TO_FULLNAME
from .mesh_export import export_basemesh, write_triangle_obj
from .modifier_request import HumanModifierRequest
from .pose_catalog import apply_pose
from .rig_export import export_rig

_HUMAN = None
# Last applied body-shape signature — skip remesh when only pose_pair changes.
_SHAPE_SIG: tuple[Any, ...] | None = None
# Rest bind + influences for current shape (reused across pose pairs).
_BIND_SHELL: dict[str, Any] | None = None
# Full generate payloads keyed by (shape_sig, pose_pair_id, pose_units, pose_id).
_GENERATE_CACHE: dict[tuple[Any, ...], dict[str, Any]] = {}
# ThreadingHTTPServer accepts concurrent POSTs; MakeHuman + globals are not re-entrant.
_GENERATE_LOCK = threading.Lock()

MODIFIER_FILES = (
    "modifiers/modeling_modifiers.json",
    "modifiers/bodyshapes_modifiers.json",
    "modifiers/measurement_modifiers.json",
)


class HumanSessionError(RuntimeError):
    pass


def _load_human():
    global _HUMAN
    if _HUMAN is not None:
        return _HUMAN
    ensure_runtime()
    import files3d
    import human
    import humanmodifier
    import skeleton
    from core import G
    from getpath import getSysDataPath

    mesh = files3d.loadMesh(getSysDataPath("3dobjs/base.obj"), maxFaces=5)
    if mesh is None:
        raise HumanSessionError("failed to load MakeHuman base.obj")
    person = human.Human(mesh)
    G.app.selectedHuman = person
    person.setBaseSkeleton(skeleton.load(getSysDataPath("rigs/default.mhskel"), person.meshData))
    for relative in MODIFIER_FILES:
        humanmodifier.loadModifiers(getSysDataPath(relative), person)
    _HUMAN = person
    return person


def _set_height_cm(person, target_cm: float) -> None:
    modifier = person.getModifier(ALIAS_TO_FULLNAME["height"])
    lo, hi = 0.0, 1.0
    for _ in range(8):
        mid = (lo + hi) / 2.0
        modifier.setValue(mid)
        person.applyAllTargets()
        got = person.getHeightCm()
        if got < target_cm:
            lo = mid
        else:
            hi = mid


def _shape_signature(request: HumanModifierRequest) -> tuple[Any, ...]:
    mods = tuple(sorted(request.modifier_values().items()))
    body = tuple(sorted((request.body_cm or {}).items()))
    height = None if request.height_cm is None else round(float(request.height_cm), 4)
    return (height, mods, body)


def _pose_units_key(pose_units: dict[str, float] | None) -> tuple[tuple[str, float], ...]:
    if not pose_units:
        return ()
    return tuple(sorted((str(k), round(float(v), 6)) for k, v in pose_units.items()))


def _cache_key(request: HumanModifierRequest, sig: tuple[Any, ...]) -> tuple[Any, ...]:
    pair = request.pose_pair_id or ""
    pose_id = request.pose_id or ""
    return (
        sig,
        bool(request.include_rig),
        pair if request.include_rig else "",
        _pose_units_key(request.pose_units),
        pose_id,
    )


def generate(payload: object) -> dict[str, Any]:
    with _GENERATE_LOCK:
        return _generate_locked(payload)


def _generate_locked(payload: object) -> dict[str, Any]:
    global _SHAPE_SIG, _BIND_SHELL
    request = (
        payload
        if isinstance(payload, HumanModifierRequest)
        else HumanModifierRequest.parse(payload)
    )
    person = _load_human()
    sig = _shape_signature(request)
    key = _cache_key(request, sig)
    cached = _GENERATE_CACHE.get(key)
    if cached is not None:
        return cached

    if _SHAPE_SIG != sig:
        person.resetMeshValues()
        for full_name, value in request.modifier_values().items():
            person.getModifier(full_name).setValue(value)
        if request.height_cm is not None:
            _set_height_cm(person, request.height_cm)
        else:
            person.applyAllTargets()
        if request.body_cm:
            apply_body_cm(person, request.body_cm)
        _SHAPE_SIG = sig
        _BIND_SHELL = None
        # Drop generate cache entries for other shapes to bound memory.
        stale = [k for k in _GENERATE_CACHE if k[0] != sig]
        for k in stale:
            del _GENERATE_CACHE[k]

    rig_payload = None
    if request.include_rig:
        pair_id = request.pose_pair_id or "tpose-to-rest"
        rig_raw = export_rig(
            person,
            pose_pair_id=pair_id,
            pose_units=request.pose_units,
            bind_shell=_BIND_SHELL,
        )
        _BIND_SHELL = rig_raw.pop("_bind_shell")
        rig_payload = rig_raw
        # OBJ must stay on the compact rig mesh; pick A or B from the pair.
        pose_key = "a"
        if request.pose_id == rig_payload["poses"]["b"]["id"]:
            pose_key = "b"
        elif request.pose_id == rig_payload["poses"]["a"]["id"]:
            pose_key = "a"
        chosen = rig_payload["poses"][pose_key]
        pose = {"id": chosen["id"], "units": {"body": {}, "face": {}}}
        obj = write_triangle_obj(
            np.asarray(chosen["posed_positions"], dtype=np.float64),
            [tuple(tri) for tri in rig_payload["bind"]["triangles"]],
        )
    else:
        pose = apply_pose(person, request.pose_id, request.pose_units)
        mesh = person.meshData
        obj = export_basemesh(mesh.coord, mesh.fvert, mesh.face_mask)

    if qt_imported():
        raise HumanSessionError("Qt was imported during generate; headless contract broken")
    result = {
        "height_cm": float(person.getHeightCm()),
        "applied": request.as_dict(),
        "pose": pose,
        "unit": "m",
        "up": "y",
        "obj": obj,
    }
    if rig_payload is not None:
        result["rig"] = rig_payload
    _GENERATE_CACHE[key] = result
    return result
