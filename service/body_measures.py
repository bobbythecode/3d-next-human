"""Accept authored body measure keys; fit MH measure rulers when known."""

from __future__ import annotations

import math
from typing import Mapping

# Authored body keys only (no `_` derived).
AUTHORED_BODY_KEYS = frozenset(
    {
        "arm_length",
        "arm_pose_angle",
        "armscye_depth",
        "back_width",
        "bum_points",
        "bust",
        "bust_line",
        "bust_points",
        "crotch_hip_diff",
        "head_l",
        "height",
        "hip_back_width",
        "hip_inclination",
        "hips",
        "hips_line",
        "leg_circ",
        "neck_w",
        "shoulder_incl",
        "shoulder_w",
        "underbust",
        "vert_bust_line",
        "waist",
        "waist_back_width",
        "waist_line",
        "waist_over_bust_line",
        "wrist",
    }
)

# Vertex-pair paths from MakeHuman plugins/0_modeling_a_measurement.py Ruler
# (copied so headless generate never imports Qt GUI plugins).
_MEASURE_PATHS: dict[str, list[int]] = {
    "measure/measure-neck-circ-decr|incr": [
        7514, 10358, 7631, 7496, 7488, 7489, 7474, 7475, 7531, 7537, 7543, 7549,
        7555, 7561, 7743, 7722, 856, 1030, 1051, 850, 844, 838, 832, 826, 820,
        756, 755, 770, 769, 777, 929, 3690, 804, 800, 808, 801, 799, 803, 7513,
        7515, 7521, 7514,
    ],
    "measure/measure-bust-circ-decr|incr": [
        8439, 8455, 8462, 8446, 8478, 8494, 8557, 8510, 8526, 8542, 10720, 10601,
        10603, 10602, 10612, 10611, 10610, 10613, 10604, 10605, 10606, 3942, 3941,
        3940, 3950, 3947, 3948, 3949, 3938, 3939, 3937, 4065, 1870, 1854, 1838,
        1885, 1822, 1806, 1774, 1790, 1783, 1767, 1799, 8471,
    ],
    "measure/measure-underbust-circ-decr|incr": [
        10750, 10744, 10724, 10725, 10748, 10722, 10640, 10642, 10641, 10651,
        10650, 10649, 10652, 10643, 10644, 10645, 10646, 10647, 10648, 3988,
        3987, 3986, 3985, 3984, 3983, 3982, 3992, 3989, 3990, 3991, 3980, 3981,
        3979, 4067, 4098, 4073, 4072, 4094, 4100, 4082, 4088, 4088,
    ],
    "measure/measure-waist-circ-decr|incr": [
        4121, 10760, 10757, 10777, 10776, 10779, 10780, 10778, 10781, 10771,
        10773, 10772, 10775, 10774, 10814, 10834, 10816, 10817, 10818, 10819,
        10820, 10821, 4181, 4180, 4179, 4178, 4177, 4176, 4175, 4196, 4173,
        4131, 4132, 4129, 4130, 4128, 4138, 4135, 4137, 4136, 4133, 4134, 4108,
        4113, 4118, 4121,
    ],
    "measure/measure-hips-circ-decr|incr": [
        4341, 10968, 10969, 10971, 10970, 10967, 10928, 10927, 10925, 10926,
        10923, 10924, 10868, 10875, 10861, 10862, 4228, 4227, 4226, 4242, 4234,
        4294, 4293, 4296, 4295, 4297, 4298, 4342, 4345, 4346, 4344, 4343, 4361,
        4341,
    ],
    "measure/measure-wrist-circ-decr|incr": [
        10208, 10211, 10212, 10216, 10471, 10533, 10213, 10214, 10215, 10205,
        10204, 10203, 10437, 10202, 10201, 10206, 10200, 10210, 10209, 10208,
    ],
    "measure/measure-shoulder-dist-decr|incr": [7478, 8274],
}

# Keys that currently drive MakeHuman measure fit (plan later for the rest).
BODY_KEY_TO_MEASURE: dict[str, str] = {
    "bust": "measure/measure-bust-circ-decr|incr",
    "waist": "measure/measure-waist-circ-decr|incr",
    "hips": "measure/measure-hips-circ-decr|incr",
    "underbust": "measure/measure-underbust-circ-decr|incr",
    "neck_w": "measure/measure-neck-circ-decr|incr",
    "wrist": "measure/measure-wrist-circ-decr|incr",
    "shoulder_w": "measure/measure-shoulder-dist-decr|incr",
}


class BodyMeasureError(ValueError):
    pass


def parse_body_cm(raw: object) -> dict[str, float]:
    if raw is None:
        return {}
    if not isinstance(raw, Mapping):
        raise BodyMeasureError("body must be a JSON object of cm measures")
    values: dict[str, float] = {}
    for key, value in raw.items():
        name = str(key)
        if name.startswith("_"):
            continue
        if name not in AUTHORED_BODY_KEYS:
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise BodyMeasureError(f"body.{name} must be a number")
        number = float(value)
        if not math.isfinite(number) or number <= 0.0 or number > 250.0:
            raise BodyMeasureError(f"body.{name} must be in (0, 250]")
        values[name] = number
    return values


def measure_cm(person, measure_id: str) -> float:
    path = _MEASURE_PATHS[measure_id]
    total = 0.0
    v1 = path[0]
    coords = person.meshData.coord
    for v2 in path:
        vec = coords[v1] - coords[v2]
        total += float(math.sqrt(float(vec.dot(vec))))
        v1 = v2
    return 10.0 * total


def set_measure_cm(person, measure_id: str, target_cm: float) -> None:
    modifier = person.getModifier(measure_id)
    lo, hi = -1.0, 1.0
    value = 0.0
    for _ in range(12):
        modifier.setValue(value)
        person.applyAllTargets()
        got = measure_cm(person, measure_id)
        if abs(got - target_cm) < 0.05:
            return
        if got < target_cm:
            lo = value
            value = value + (hi - value) / 2.0
        else:
            hi = value
            value = lo + (value - lo) / 2.0
    modifier.setValue(value)
    person.applyAllTargets()


def apply_body_cm(person, body_cm: Mapping[str, float]) -> dict[str, float]:
    """Fit known MH measures; other authored keys are carried in applied only."""
    fitted: dict[str, float] = {}
    for key, target in body_cm.items():
        if key == "height":
            continue
        measure_id = BODY_KEY_TO_MEASURE.get(key)
        if measure_id is None:
            continue
        set_measure_cm(person, measure_id, target)
        fitted[key] = float(target)
    return fitted
