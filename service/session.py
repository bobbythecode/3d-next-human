"""Apply macros on a headless MakeHuman Human and export OBJ metres Y-up."""

from __future__ import annotations

from typing import Any

from .bootstrap import ensure_runtime, qt_imported
from .catalog import ALIAS_TO_FULLNAME
from .mesh_export import export_basemesh
from .modifier_request import HumanModifierRequest

_HUMAN = None

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
    from getpath import getSysDataPath

    mesh = files3d.loadMesh(getSysDataPath("3dobjs/base.obj"), maxFaces=5)
    if mesh is None:
        raise HumanSessionError("failed to load MakeHuman base.obj")
    person = human.Human(mesh)
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


def generate(payload: object) -> dict[str, Any]:
    request = (
        payload
        if isinstance(payload, HumanModifierRequest)
        else HumanModifierRequest.parse(payload)
    )
    person = _load_human()
    person.resetMeshValues()
    for full_name, value in request.modifier_values().items():
        person.getModifier(full_name).setValue(value)
    if request.height_cm is not None:
        _set_height_cm(person, request.height_cm)
    else:
        person.applyAllTargets()
    if qt_imported():
        raise HumanSessionError("Qt was imported during generate; headless contract broken")
    mesh = person.meshData
    obj = export_basemesh(mesh.coord, mesh.fvert, mesh.face_mask)
    return {
        "height_cm": float(person.getHeightCm()),
        "applied": request.as_dict(),
        "unit": "m",
        "up": "y",
        "obj": obj,
    }
