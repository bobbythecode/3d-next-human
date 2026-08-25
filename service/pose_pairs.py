"""Curated pose-pair catalog for P9 Phase 1 transitions."""

from __future__ import annotations

from typing import Any

from .pose_catalog import REST_POSE_ID, allowed_pose_ids

CATALOG_VERSION = "pose-pairs.v1"
RIG_ID = "mh-default"
RIG_VERSION = "1"

# Golden pairs — not the full combinatorial library.
_PAIRS: tuple[dict[str, Any], ...] = (
    {
        "id": "tpose-to-rest",
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


def pose_pair_endpoints(pair: dict[str, Any]) -> tuple[str, str]:
    a_id = str(pair["a"]["pose"]["id"])
    b_id = str(pair["b"]["pose"]["id"])
    allowed = allowed_pose_ids()
    if a_id not in allowed:
        raise KeyError(f"pose pair A unknown: {a_id}")
    if b_id not in allowed:
        raise KeyError(f"pose pair B unknown: {b_id}")
    return a_id, b_id
