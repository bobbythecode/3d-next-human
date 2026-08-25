"""Export versioned human-rig.v1 payload (joints · inv-bind · LBS weights · pose pair)."""

from __future__ import annotations

from typing import Any

import numpy as np
import numpy.linalg as la

from .mesh_export import DM_TO_M, collect_body_triangles, compact_used, place_feet_on_ground
from .pose_catalog import apply_pose
from .pose_pairs import RIG_ID, RIG_VERSION, get_pose_pair, pose_pair_endpoints

SCHEMA = "human-rig.v1"
MAX_INFLUENCES = 6
MESH_ORIENTATION = "yUpFaceZ"
LOCAL_BONE_AXIS = "y"


def _mat4_list(mat: np.ndarray) -> list[list[float]]:
    m = np.asarray(mat, dtype=np.float64)
    if m.shape != (4, 4):
        raise ValueError("expected 4x4 matrix")
    return [[float(m[r, c]) for c in range(4)] for r in range(4)]


def _scale_affine_dm_to_m(mat: np.ndarray) -> np.ndarray:
    out = np.asarray(mat, dtype=np.float64).copy()
    out[:3, 3] *= DM_TO_M
    return out


def _apply_y_translation(mat: np.ndarray, dy: float) -> np.ndarray:
    out = np.asarray(mat, dtype=np.float64).copy()
    out[1, 3] += float(dy)
    return out


def _compiled_influences(person, skel, n_weights: int = MAX_INFLUENCES) -> tuple[np.ndarray, np.ndarray]:
    weights = person.getVertexWeights(skel)
    compiled = weights.compiled(nWeights=n_weights, skel=skel)
    if compiled is None:
        raise RuntimeError("failed to compile vertex bone weights")
    n = int(compiled.shape[0])
    indices = np.zeros((n, n_weights), dtype=np.int32)
    values = np.zeros((n, n_weights), dtype=np.float64)
    for k in range(n_weights):
        indices[:, k] = compiled[f"b_idx{k + 1}"]
        values[:, k] = compiled[f"wght{k + 1}"]
    return indices, values


def _remap_influences(
    indices: np.ndarray,
    values: np.ndarray,
    used_old: list[int],
) -> tuple[list[list[int]], list[list[float]]]:
    joint_indices: list[list[int]] = []
    joint_weights: list[list[float]] = []
    for old in used_old:
        row_i = indices[old]
        row_w = values[old]
        total = float(np.sum(row_w))
        if total > 1e-12:
            row_w = row_w / total
        joint_indices.append([int(x) for x in row_i.tolist()])
        joint_weights.append([float(x) for x in row_w.tolist()])
    return joint_indices, joint_weights


def _capture_joint_world_m(skel, ground_offset_dm: float) -> list[list[list[float]]]:
    mats: list[list[list[float]]] = []
    for bone in skel.getBones():
        global_dm = _apply_y_translation(bone.matPoseGlobal, -ground_offset_dm)
        mats.append(_mat4_list(_scale_affine_dm_to_m(global_dm)))
    return mats


def _capture_joint_local_m(skel, ground_offset_dm: float) -> list[list[list[float]]]:
    """Parent-relative pose matrices in metres (grounded)."""
    world = []
    for bone in skel.getBones():
        global_dm = _apply_y_translation(bone.matPoseGlobal, -ground_offset_dm)
        world.append(_scale_affine_dm_to_m(global_dm))
    locals_m: list[list[list[float]]] = []
    bones = skel.getBones()
    for bone, w in zip(bones, world):
        if bone.parent is None:
            locals_m.append(_mat4_list(w))
            continue
        parent_w = world[bone.parent.index]
        local = la.inv(parent_w) @ w
        locals_m.append(_mat4_list(local))
    return locals_m


def _joint_table(skel, ground_offset_dm: float) -> list[dict[str, Any]]:
    joints: list[dict[str, Any]] = []
    for bone in skel.getBones():
        # Use matRestGlobal (same basis as matPoseGlobal / matPoseVerts), not
        # getRestMatrix exporter remap — so LBS matches MakeHuman skinMesh.
        rest_dm = _apply_y_translation(bone.matRestGlobal, -ground_offset_dm)
        rest_m = _scale_affine_dm_to_m(rest_dm)
        inv_bind = la.inv(rest_m)
        parent_name = bone.parent.name if bone.parent is not None else None
        joints.append(
            {
                "name": bone.name,
                "parent": parent_name,
                "index": int(bone.index),
                "rest_global": _mat4_list(rest_m),
                "inverse_bind": _mat4_list(inv_bind),
            }
        )
    return joints


def export_rig(
    person,
    *,
    pose_pair_id: str,
    pose_units: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Build human-rig.v1 after morphs are applied; leaves person posed at pair A."""
    units = dict(pose_units or {})
    pair = get_pose_pair(pose_pair_id)
    pose_a, pose_b = pose_pair_endpoints(pair)

    apply_pose(person, "rest", {})
    mesh = person.meshData
    skel = person.getBaseSkeleton()
    skel.updateJoints(mesh)
    skel.build()

    triangles = collect_body_triangles(mesh.fvert, mesh.face_mask)
    used_flat = [index for tri in triangles for index in tri]
    rest_dm = np.asarray(person.getRestposeCoordinates(), dtype=np.float64).copy()
    rest_grounded = place_feet_on_ground(rest_dm, used_flat)
    used_ids = np.fromiter(used_flat, dtype=np.int64)
    ground_offset_dm = float(np.min(rest_dm[used_ids, 1]))

    coords_m, compact_tris = compact_used(rest_grounded * DM_TO_M, triangles)
    used_old = sorted({index for tri in triangles for index in tri})
    if coords_m.shape[0] != len(used_old):
        raise RuntimeError("compact vertex count mismatch")

    indices_full, weights_full = _compiled_influences(person, skel, MAX_INFLUENCES)
    joint_indices, joint_weights = _remap_influences(indices_full, weights_full, used_old)
    joints = _joint_table(skel, ground_offset_dm)

    apply_pose(person, pose_a, units)
    skel = person.getBaseSkeleton()
    world_a = _capture_joint_world_m(skel, ground_offset_dm)
    local_a = _capture_joint_local_m(skel, ground_offset_dm)
    posed_a_dm = np.asarray(mesh.coord, dtype=np.float64).copy()
    posed_a_dm[:, 1] -= ground_offset_dm
    posed_a_m, _ = compact_used(posed_a_dm * DM_TO_M, triangles)

    apply_pose(person, pose_b, units)
    skel = person.getBaseSkeleton()
    world_b = _capture_joint_world_m(skel, ground_offset_dm)
    local_b = _capture_joint_local_m(skel, ground_offset_dm)
    posed_b_dm = np.asarray(mesh.coord, dtype=np.float64).copy()
    posed_b_dm[:, 1] -= ground_offset_dm
    posed_b_m, _ = compact_used(posed_b_dm * DM_TO_M, triangles)

    # Leave person at pose A for OBJ export in session.generate
    apply_pose(person, pose_a, units)

    return {
        "schema": SCHEMA,
        "rig_id": RIG_ID,
        "rig_version": RIG_VERSION,
        "joints": joints,
        "influences": {
            "max": MAX_INFLUENCES,
            "joint_indices": joint_indices,
            "weights": joint_weights,
            "vertex_count": int(coords_m.shape[0]),
            "vertex_map": used_old,
        },
        "bind": {
            "rest_positions": coords_m.astype(np.float64).tolist(),
            "triangles": [list(tri) for tri in compact_tris],
        },
        "poses": {
            "a": {
                "id": pose_a,
                "world_matrices": world_a,
                "local_matrices": local_a,
                "posed_positions": posed_a_m.astype(np.float64).tolist(),
            },
            "b": {
                "id": pose_b,
                "world_matrices": world_b,
                "local_matrices": local_b,
                "posed_positions": posed_b_m.astype(np.float64).tolist(),
            },
        },
        "pose_pair": {
            "id": pair["id"],
            "version": pair["version"],
            "duration_s": pair["duration_s"],
            "fps": pair["fps"],
            "interpolation": pair["interpolation"],
            "root_policy": pair["root_policy"],
        },
        "space": {
            "unit": "m",
            "up": "y",
            "feet_on_ground": True,
            "orientation": MESH_ORIENTATION,
        },
        "license": pair.get("license"),
    }
