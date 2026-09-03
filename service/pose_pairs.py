"""Curated pose-pair catalog for P9 transitions (A→B)."""

from __future__ import annotations

from typing import Any

from .pose_catalog import REST_POSE_ID, allowed_pose_ids, pose_units_map

CATALOG_VERSION = "pose-pairs.v1"
RIG_ID = "mh-default"
RIG_VERSION = "1"

# Left arm (+ hand) chain — replace from rest onto tpose for one-sided A-pose arm.
_LEFT_ARM_BONES: tuple[str, ...] = (
    "clavicle.L",
    "shoulder01.L",
    "upperarm01.L",
    "upperarm02.L",
    "lowerarm01.L",
    "lowerarm02.L",
    "wrist.L",
    "metacarpal1.L",
    "metacarpal2.L",
    "metacarpal3.L",
    "metacarpal4.L",
    "finger1-1.L",
    "finger1-2.L",
    "finger1-3.L",
    "finger2-1.L",
    "finger2-2.L",
    "finger2-3.L",
    "finger3-1.L",
    "finger3-2.L",
    "finger3-3.L",
    "finger4-1.L",
    "finger4-2.L",
    "finger4-3.L",
    "finger5-1.L",
    "finger5-2.L",
    "finger5-3.L",
)

_RIGHT_ARM_BONES: tuple[str, ...] = tuple(
    name.replace(".L", ".R") for name in _LEFT_ARM_BONES
)
# Keep T-pose arms when B is a rest-authored full BVH (e.g. kick).
_BOTH_ARM_BONES: tuple[str, ...] = (*_LEFT_ARM_BONES, *_RIGHT_ARM_BONES)

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
        "id": "tpose-to-left-arm-down",
        "name": "T-pose → left arm down",
        # v2: UpperArmDownLeft on tpose raised the arm — replace left chain from rest.
        "version": "2",
        "a": {"pose": {"id": "tpose"}},
        "b": {
            "pose": {
                "id": "tpose",
                "replace_bones": {
                    "from": {"id": REST_POSE_ID},
                    "bones": list(_LEFT_ARM_BONES),
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
        "id": "tpose-to-torso-lean",
        "name": "T-pose → torso lean",
        "version": "1",
        "a": {"pose": {"id": "tpose"}},
        "b": {
            "pose": {
                "id": "tpose",
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
        "id": "tpose-to-left-knee-bend",
        "name": "T-pose → left knee bend",
        "version": "1",
        "a": {"pose": {"id": "tpose"}},
        "b": {
            "pose": {
                "id": "tpose",
                "units": {
                    # Same units as rest-to-left-knee-bend (v2) — shin via FootTurnOutLeft.
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
        "id": "tpose-to-left-kick",
        "name": "T-pose → left kick",
        # v2: plain kick BVH drops arms to rest/A — keep T arms via replace_bones.
        "version": "2",
        "a": {"pose": {"id": "tpose"}},
        "b": {
            "pose": {
                "id": "kick",
                "replace_bones": {
                    "from": {"id": "tpose"},
                    "bones": list(_BOTH_ARM_BONES),
                },
            }
        },
        "duration_s": 1.0,
        "fps": 30,
        "interpolation": "joint_local_slerp",
        "root_policy": "lock_feet",
        "license": {
            "assets": "CC0-1.0",
            "note": "author BVH in makehuman/data/poses/",
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
        "version": "2",
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


def _endpoint_pose(
    endpoint: dict[str, Any],
) -> tuple[str, dict[str, float], str | None, tuple[str, ...]]:
    pose = endpoint["pose"]
    pose_id = str(pose["id"])
    raw_units = pose.get("units") or {}
    units = {str(k): float(v) for k, v in dict(raw_units).items() if float(v) > 0}
    replace = pose.get("replace_bones") or {}
    replace_from: str | None = None
    replace_bones: tuple[str, ...] = ()
    if replace:
        from_pose = replace.get("from") or {}
        replace_from = str(from_pose.get("id") or "") or None
        raw_bones = replace.get("bones") or []
        replace_bones = tuple(str(name) for name in list(raw_bones) if str(name))
    return pose_id, units, replace_from, replace_bones


def pose_pair_endpoints(
    pair: dict[str, Any],
) -> tuple[
    tuple[str, dict[str, float], str | None, tuple[str, ...]],
    tuple[str, dict[str, float], str | None, tuple[str, ...]],
]:
    """Return ((pose_a, units_a, replace_from_a, bones_a), …B…)."""
    a_id, a_units, a_from, a_bones = _endpoint_pose(pair["a"])
    b_id, b_units, b_from, b_bones = _endpoint_pose(pair["b"])
    allowed = allowed_pose_ids()
    known_units = pose_units_map()
    if a_id not in allowed:
        raise KeyError(f"pose pair A unknown: {a_id}")
    if b_id not in allowed:
        raise KeyError(f"pose pair B unknown: {b_id}")
    for src in (a_from, b_from):
        if src is not None and src not in allowed:
            raise KeyError(f"pose pair replace_bones_from unknown: {src}")
    for unit_id in (*a_units, *b_units):
        if unit_id not in known_units:
            raise KeyError(f"pose pair unit unknown: {unit_id}")
    return (a_id, a_units, a_from, a_bones), (b_id, b_units, b_from, b_bones)


def main(argv: list[str] | None = None) -> int:
    import json
    import sys

    args = list(sys.argv[1:] if argv is None else argv)
    try:
        payload = get_pose_pair(args[0]) if args else pose_pairs_payload()
    except KeyError as err:
        print(str(err), file=sys.stderr)
        return 1
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
