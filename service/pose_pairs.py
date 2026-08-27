"""Curated pose-pair catalog for P9 transitions (A→B)."""

from __future__ import annotations

from typing import Any

from .pose_catalog import REST_POSE_ID, allowed_pose_ids, pose_units_map

CATALOG_VERSION = "pose-pairs.v1"
RIG_ID = "mh-default"
RIG_VERSION = "1"

# Golden pairs — not the full combinatorial library.
# Endpoints may add poseunit weights on top of a library pose id (usually rest).
_PAIRS: tuple[dict[str, Any], ...] = (
    {
        "id": "tpose-to-rest",
        "name": "T-pose → rest",
        "version": "1",
        "a": {"pose": {"id": "tpose"}},
        "b": {"pose": {"id": REST_POSE_ID}},
        "duration_s": 1.0,
        "fps": 30,
        "interpolation": "joint_local_slerp",
        "root_policy": "lock_feet",
        "license": {
            "assets": "CC0-1.0",
            "note": "bundled MakeHuman poses / poseunits (LICENSE.md §C)",
        },
    },
    {
        "id": "rest-to-tpose",
        "name": "rest → T-pose",
        "version": "1",
        "a": {"pose": {"id": REST_POSE_ID}},
        "b": {"pose": {"id": "tpose"}},
        "duration_s": 1.0,
        "fps": 30,
        "interpolation": "joint_local_slerp",
        "root_policy": "lock_feet",
        "license": {
            "assets": "CC0-1.0",
            "note": "bundled MakeHuman poses / poseunits (LICENSE.md §C)",
        },
    },
    {
        "id": "rest-to-left-arm-up",
        "name": "rest → left arm up",
        "version": "2",
        "a": {"pose": {"id": REST_POSE_ID}},
        "b": {
            "pose": {
                "id": REST_POSE_ID,
                "units": {
                    # MH body-poseunits.json: UpperArmUpLeft* only touches face oris_* —
                    # use Forward+RollOut which actually lift wrist.L (~40cm).
                    "UpperArmForwardLeft": 1.0,
                    "UpperArmRollOutLeft": 0.55,
                },
            }
        },
        "duration_s": 1.0,
        "fps": 30,
        "interpolation": "joint_local_slerp",
        "root_policy": "lock_feet",
        "license": {
            "assets": "CC0-1.0",
            "note": "bundled MakeHuman poses / poseunits (LICENSE.md §C)",
        },
    },
    {
        "id": "rest-to-torso-lean",
        "name": "rest → torso lean",
        "version": "1",
        "a": {"pose": {"id": REST_POSE_ID}},
        "b": {
            "pose": {
                "id": REST_POSE_ID,
                "units": {"TorsoLeft": 0.9},
            }
        },
        "duration_s": 1.0,
        "fps": 30,
        "interpolation": "joint_local_slerp",
        "root_policy": "lock_feet",
        "license": {
            "assets": "CC0-1.0",
            "note": "bundled MakeHuman poses / poseunits (LICENSE.md §C)",
        },
    },
    {
        "id": "rest-to-left-knee-bend",
        "name": "rest → left knee bend",
        "version": "2",
        "a": {"pose": {"id": REST_POSE_ID}},
        "b": {
            "pose": {
                "id": REST_POSE_ID,
                "units": {
                    # MH body-poseunits: LowerLegBendLeft* only rotate upperleg.L
                    # (no shin). FootTurnOutLeft rotates lowerleg01.L (~knee bend).
                    "UpperLegForwardLeft": 0.7,
                    "FootTurnOutLeft": 0.55,
                },
            }
        },
        "duration_s": 1.0,
        "fps": 30,
        "interpolation": "joint_local_slerp",
        "root_policy": "lock_feet",
        "license": {
            "assets": "CC0-1.0",
            "note": "bundled MakeHuman poses / poseunits (LICENSE.md §C)",
        },
    },
    {
        "id": "rest-to-kick",
        "name": "rest → kick",
        "version": "1",
        "a": {"pose": {"id": REST_POSE_ID}},
        "b": {"pose": {"id": "kick"}},
        "duration_s": 1.0,
        "fps": 30,
        "interpolation": "joint_local_slerp",
        "root_policy": "lock_feet",
        "license": {
            "assets": "CC0-1.0",
            "note": "author BVH in makehuman/data/poses/",
        },
    },
)


def pose_pairs_payload() -> dict[str, Any]:
    return {
        "version": CATALOG_VERSION,
        "rig": {"id": RIG_ID, "version": RIG_VERSION},
        "pairs": [dict(item) for item in _PAIRS],
    }


def get_pose_pair(pair_id: str) -> dict[str, Any]:
    for item in _PAIRS:
        if item["id"] == pair_id:
            return dict(item)
    raise KeyError(f"unknown pose_pair_id: {pair_id}")


def _endpoint_pose(endpoint: dict[str, Any]) -> tuple[str, dict[str, float]]:
    pose = endpoint["pose"]
    pose_id = str(pose["id"])
    raw_units = pose.get("units") or {}
    units = {str(k): float(v) for k, v in dict(raw_units).items() if float(v) > 0}
    return pose_id, units


def pose_pair_endpoints(
    pair: dict[str, Any],
) -> tuple[tuple[str, dict[str, float]], tuple[str, dict[str, float]]]:
    """Return ((pose_a_id, units_a), (pose_b_id, units_b))."""
    a_id, a_units = _endpoint_pose(pair["a"])
    b_id, b_units = _endpoint_pose(pair["b"])
    allowed = allowed_pose_ids()
    known_units = pose_units_map()
    if a_id not in allowed:
        raise KeyError(f"pose pair A unknown: {a_id}")
    if b_id not in allowed:
        raise KeyError(f"pose pair B unknown: {b_id}")
    for unit_id in (*a_units, *b_units):
        if unit_id not in known_units:
            raise KeyError(f"pose pair unit unknown: {unit_id}")
    return (a_id, a_units), (b_id, b_units)
