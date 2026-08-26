"""Pose catalog and pose application helpers for headless human-api."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

POSES_DIR = Path(__file__).resolve().parents[1] / "makehuman" / "data" / "poses"
POSEUNITS_DIR = Path(__file__).resolve().parents[1] / "makehuman" / "data" / "poseunits"
COMPARE_BONE = "upperleg02.L"
REST_POSE_ID = "rest"

_BODY_POSEUNITS: dict[str, dict[str, tuple[float, float, float, float]]] | None = None
_FACE_POSEUNIT_NAMES: list[str] | None = None

# body-poseunits.json still names some bones as upperleg.L/.R; default MH
# skeleton uses upperleg01 + upperleg02. Map the old name to the proximal bone.
_BONE_ALIASES = {
    "upperleg.L": "upperleg01.L",
    "upperleg.R": "upperleg01.R",
}


def _resolve_bone_index(bone_index: dict[str, int], bone_name: str) -> int | None:
    if bone_name in bone_index:
        return bone_index[bone_name]
    alias = _BONE_ALIASES.get(bone_name)
    if alias is not None and alias in bone_index:
        return bone_index[alias]
    return None


def _list_pose_ids() -> list[str]:
    ids = sorted(path.stem.lower() for path in POSES_DIR.glob("*.bvh"))
    return [REST_POSE_ID, *ids]


def _load_body_poseunits() -> dict[str, dict[str, tuple[float, float, float, float]]]:
    global _BODY_POSEUNITS
    if _BODY_POSEUNITS is not None:
        return _BODY_POSEUNITS
    payload = json.loads((POSEUNITS_DIR / "body-poseunits.json").read_text(encoding="utf-8"))
    poses = payload.get("poses") or {}
    data: dict[str, dict[str, tuple[float, float, float, float]]] = {}
    for unit_id, bone_map in poses.items():
        item: dict[str, tuple[float, float, float, float]] = {}
        for bone_name, quat in (bone_map or {}).items():
            if not isinstance(quat, list) or len(quat) != 4:
                continue
            item[str(bone_name)] = (
                float(quat[0]),
                float(quat[1]),
                float(quat[2]),
                float(quat[3]),
            )
        data[str(unit_id)] = item
    _BODY_POSEUNITS = data
    return data


def _load_face_poseunit_names() -> list[str]:
    global _FACE_POSEUNIT_NAMES
    if _FACE_POSEUNIT_NAMES is not None:
        return _FACE_POSEUNIT_NAMES
    payload = json.loads((POSEUNITS_DIR / "face-poseunits.json").read_text(encoding="utf-8"))
    mapping = [str(item) for item in payload.get("framemapping") or []]
    _FACE_POSEUNIT_NAMES = mapping
    return mapping


def allowed_pose_ids() -> frozenset[str]:
    return frozenset(_list_pose_ids())


def pose_units_map() -> dict[str, str]:
    units: dict[str, str] = {}
    for unit_id in _load_body_poseunits().keys():
        units[unit_id] = "body"
    for unit_id in _load_face_poseunit_names():
        if unit_id.lower() == "rest":
            continue
        units[unit_id] = "face"
    return units


def pose_catalog_payload() -> dict[str, Any]:
    library = [{"id": pose_id, "name": pose_id} for pose_id in _list_pose_ids()]
    units = [
        {"id": unit_id, "group": group}
        for unit_id, group in sorted(pose_units_map().items(), key=lambda item: item[0].lower())
    ]
    return {"library": library, "units": units}


def _load_bvh_animation(person, pose_id: str):
    if pose_id == REST_POSE_ID:
        return None
    import bvh
    from getpath import getSysDataPath

    filepath = getSysDataPath(f"poses/{pose_id}.bvh")
    bvh_file = bvh.load(filepath, convertFromZUp="auto")
    if COMPARE_BONE not in bvh_file.joints:
        raise RuntimeError(f"pose {pose_id} does not use the default MakeHuman rig")
    anim = bvh_file.createAnimationTrack(person.getBaseSkeleton(), name=f"pose-{pose_id}")
    _autoscale_bvh_root_translation(person, bvh_file, anim)
    return anim


def _autoscale_bvh_root_translation(person, bvh_file, anim) -> None:
    import numpy.linalg as la

    if "root" not in bvh_file.joints:
        return
    bvh_joint = bvh_file.joints[COMPARE_BONE]
    bvh_length = la.norm(bvh_joint.children[0].position - bvh_joint.position)
    if bvh_length <= 1e-9:
        return
    posedata = anim.getAtFramePos(0, noBake=True)
    root_translation = posedata[0, :3, 3].copy()
    bone = person.getBaseSkeleton().getBone(COMPARE_BONE)
    scale = float(bone.length) / float(bvh_length)
    posedata[0, :3, 3] = scale * root_translation
    anim.resetBaked()


def _load_face_poseunit(person):
    import animation
    import bvh
    from getpath import getSysDataPath

    pose_names = _load_face_poseunit_names()
    base_bvh = bvh.load(getSysDataPath("poseunits/face-poseunits.bvh"), allowTranslation="none")
    base_anim = base_bvh.createAnimationTrack(person.getBaseSkeleton(), name="poseunits-face")
    if len(pose_names) != base_bvh.frameCount:
        raise RuntimeError(
            f"face poseunits frame mismatch: bvh={base_bvh.frameCount} json={len(pose_names)}"
        )
    return animation.PoseUnit(base_anim.name, base_anim._data, pose_names)


def _pose_data_for_units(person, unit_weights: dict[str, float]):
    import animation
    import transformations as tm

    n_bones = len(person.getBaseSkeleton().getBones())
    if not unit_weights:
        return animation.emptyPose(n_bones), {"body": {}, "face": {}}

    body_defs = _load_body_poseunits()
    face_poseunit = _load_face_poseunit(person)
    bones = person.getBaseSkeleton().getBones()
    bone_index = {bone.name: idx for idx, bone in enumerate(bones)}

    unit_data = animation.emptyPose(n_bones)
    body_used: dict[str, float] = {}
    face_used: dict[str, float] = {}
    rest_quat = np.asarray([1, 0, 0, 0], dtype=np.float32)
    m = np.identity(4, dtype=np.float32)

    def apply_weighted_quat(bone_idx: int, quat: np.ndarray, weight: float) -> None:
        if weight <= 0:
            return
        m[:3, :4] = unit_data[bone_idx]
        current_quat = tm.quaternion_from_matrix(m, True)
        weighted = tm.quaternion_slerp(rest_quat, quat, float(weight))
        merged = tm.quaternion_multiply(weighted, current_quat)
        unit_data[bone_idx] = tm.quaternion_matrix(merged)[:3, :4]

    for unit_id, weight in unit_weights.items():
        if unit_id in body_defs:
            body_used[unit_id] = weight
            for bone_name, quat in body_defs[unit_id].items():
                idx = _resolve_bone_index(bone_index, bone_name)
                if idx is None:
                    continue
                apply_weighted_quat(idx, np.asarray(quat, dtype=np.float32), weight)
            continue
        if unit_id in face_poseunit.getPoseNames():
            face_used[unit_id] = weight
            pose = face_poseunit.getUnitPose(unit_id)
            for idx in range(n_bones):
                m[:3, :4] = pose[idx]
                quat = tm.quaternion_from_matrix(m, True)
                apply_weighted_quat(idx, quat, weight)
            continue
        raise RuntimeError(f"unknown pose unit: {unit_id}")
    return unit_data, {"body": body_used, "face": face_used}


def apply_pose(person, pose_id: str, pose_units: dict[str, float]) -> dict[str, Any]:
    import animation
    import transformations as tm

    person.resetToRestPose(update=False)
    person.setPosed(False)

    anim = _load_bvh_animation(person, pose_id)
    if anim is not None:
        person.addAnimation(anim)
        person.setActiveAnimation(anim.name)
        person.setToFrame(0, update=False)
        person.setPosed(True)
        person.refreshPose(updateIfInRest=False)

    if person.getActiveAnimation() is None:
        base = animation.emptyPose(len(person.getBaseSkeleton().getBones()))
    else:
        base = person.getPoseState(noBake=True)
    unit_data, used = _pose_data_for_units(person, pose_units)
    if pose_units:
        n_bones = len(person.getBaseSkeleton().getBones())
        merged = base.copy()
        m = np.identity(4, dtype=np.float32)
        for idx in range(n_bones):
            m[:3, :4] = base[idx]
            base_quat = tm.quaternion_from_matrix(m, True)
            m[:3, :4] = unit_data[idx]
            unit_quat = tm.quaternion_from_matrix(m, True)
            merged_quat = tm.quaternion_multiply(unit_quat, base_quat)
            merged[idx] = tm.quaternion_matrix(merged_quat)[:3, :4]
        pose = animation.Pose("pose-library-units", merged)
        person.addAnimation(pose)
        person.setActiveAnimation(pose.name)
        person.setToFrame(0, update=False)
        person.setPosed(True)
        person.refreshPose(updateIfInRest=False)

    return {"id": pose_id, "units": used}
