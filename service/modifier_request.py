"""Parse MakeHuman macros and modifier fullNames for generate."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional

from .catalog import ALIAS_TO_FULLNAME, ETHNIC_IDS, MACRO_IDS, allowed_modifier_ids
from .pose_catalog import REST_POSE_ID, allowed_pose_ids, pose_units_map

MACRO_KEYS = ("gender", "age", "weight", "muscle")
HEIGHT_KEYS = ("height", "height_cm")
TOP_LEVEL = frozenset(
    MACRO_KEYS
    + HEIGHT_KEYS
    + ("proportions", "african", "asian", "caucasian", "modifiers", "pose", "pose_units")
)


class ModifierRequestError(ValueError):
    pass


def _as_number(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ModifierRequestError(f"{name} must be a number")
    return float(value)


def _as_unit(value: Any, name: str) -> float:
    number = _as_number(value, name)
    if number < 0.0 or number > 1.0:
        raise ModifierRequestError(f"{name} must be between 0 and 1")
    return number


def _as_signed(value: Any, name: str) -> float:
    number = _as_number(value, name)
    if number < -1.0 or number > 1.0:
        raise ModifierRequestError(f"{name} must be between -1 and 1")
    return number


def _as_cm(value: Any) -> float:
    number = _as_number(value, "height_cm")
    if number <= 0.0 or number > 250.0:
        raise ModifierRequestError("height_cm must be in (0, 250]")
    return number


def _clamp_modifier(slider_id: str, value: Any) -> float:
    if slider_id in MACRO_IDS or slider_id in ETHNIC_IDS:
        return _as_unit(value, slider_id)
    return _as_signed(value, slider_id)


@dataclass(frozen=True)
class HumanModifierRequest:
    gender: float = 0.5
    age: float = 0.5
    weight: float = 0.5
    muscle: float = 0.5
    height: Optional[float] = 0.5
    height_cm: Optional[float] = None
    proportions: float = 0.5
    african: float = 1.0 / 3.0
    asian: float = 1.0 / 3.0
    caucasian: float = 1.0 / 3.0
    extra: dict[str, float] = field(default_factory=dict)
    pose_id: str = REST_POSE_ID
    pose_units: dict[str, float] = field(default_factory=dict)

    @classmethod
    def parse(cls, payload: object) -> "HumanModifierRequest":
        if payload is None:
            payload = {}
        if not isinstance(payload, Mapping):
            raise ModifierRequestError("body must be a JSON object")
        unknown = [key for key in payload.keys() if key not in TOP_LEVEL]
        if unknown:
            raise ModifierRequestError(
                "unknown fields: " + ", ".join(sorted(str(k) for k in unknown))
            )
        if "height" in payload and "height_cm" in payload:
            raise ModifierRequestError("send height or height_cm, not both")

        allowed = allowed_modifier_ids()
        extra: dict[str, float] = {}
        raw_modifiers = payload.get("modifiers")
        if raw_modifiers is not None:
            if not isinstance(raw_modifiers, Mapping):
                raise ModifierRequestError("modifiers must be a JSON object")
            for key, value in raw_modifiers.items():
                name = str(key)
                if name not in allowed:
                    raise ModifierRequestError(f"unknown modifier: {name}")
                extra[name] = _clamp_modifier(name, value)

        values = {key: _as_unit(payload[key], key) for key in MACRO_KEYS if key in payload}
        height: Optional[float] = 0.5
        height_cm: Optional[float] = None
        if "height_cm" in payload:
            height = None
            height_cm = _as_cm(payload["height_cm"])
        elif "height" in payload:
            height = _as_unit(payload["height"], "height")
        elif ALIAS_TO_FULLNAME["height"] in extra:
            height = extra[ALIAS_TO_FULLNAME["height"]]

        if height_cm is not None and ALIAS_TO_FULLNAME["height"] in extra:
            raise ModifierRequestError("send height or height_cm, not both")

        optional_aliases = ("proportions", "african", "asian", "caucasian")
        extras_alias = {
            key: _as_unit(payload[key], key) for key in optional_aliases if key in payload
        }
        pose_id = _parse_pose(payload.get("pose"))
        pose_units = _parse_pose_units(payload.get("pose_units"))
        return cls(
            height=height,
            height_cm=height_cm,
            extra=extra,
            pose_id=pose_id,
            pose_units=pose_units,
            **values,
            **extras_alias,
        )

    def as_dict(self) -> dict[str, float]:
        payload: dict[str, float] = {
            "gender": self.gender,
            "age": self.age,
            "weight": self.weight,
            "muscle": self.muscle,
            "proportions": self.proportions,
            "african": self.african,
            "asian": self.asian,
            "caucasian": self.caucasian,
        }
        if self.height_cm is not None:
            payload["height_cm"] = self.height_cm
        else:
            payload["height"] = float(self.height if self.height is not None else 0.5)
        payload.update(self.extra)
        if self.pose_id != REST_POSE_ID:
            payload["pose"] = {"id": self.pose_id}
        if self.pose_units:
            payload["pose_units"] = dict(self.pose_units)
        return payload

    def modifier_values(self) -> dict[str, float]:
        values = {
            ALIAS_TO_FULLNAME["gender"]: self.gender,
            ALIAS_TO_FULLNAME["age"]: self.age,
            ALIAS_TO_FULLNAME["weight"]: self.weight,
            ALIAS_TO_FULLNAME["muscle"]: self.muscle,
            ALIAS_TO_FULLNAME["proportions"]: self.proportions,
            ALIAS_TO_FULLNAME["african"]: self.african,
            ALIAS_TO_FULLNAME["asian"]: self.asian,
            ALIAS_TO_FULLNAME["caucasian"]: self.caucasian,
        }
        if self.height is not None:
            values[ALIAS_TO_FULLNAME["height"]] = self.height
        values.update(self.extra)
        if self.height_cm is not None:
            values.pop(ALIAS_TO_FULLNAME["height"], None)
        _normalize_ethnic(values)
        return values


def _normalize_ethnic(values: dict[str, float]) -> None:
    total = sum(values.get(slider_id, 0.0) for slider_id in ETHNIC_IDS)
    if total <= 1e-9:
        share = 1.0 / len(ETHNIC_IDS)
        for slider_id in ETHNIC_IDS:
            values[slider_id] = share
        return
    for slider_id in ETHNIC_IDS:
        values[slider_id] = values.get(slider_id, 0.0) / total


def _parse_pose(raw_pose: Any) -> str:
    if raw_pose is None:
        return REST_POSE_ID
    if not isinstance(raw_pose, Mapping):
        raise ModifierRequestError("pose must be an object like { id: \"tpose\" }")
    raw_id = raw_pose.get("id")
    if not isinstance(raw_id, str) or raw_id.strip() == "":
        raise ModifierRequestError("pose.id must be a non-empty string")
    pose_id = raw_id.strip().lower()
    if pose_id not in allowed_pose_ids():
        raise ModifierRequestError(f"unknown pose id: {pose_id}")
    return pose_id


def _parse_pose_units(raw_units: Any) -> dict[str, float]:
    if raw_units is None:
        return {}
    if not isinstance(raw_units, Mapping):
        raise ModifierRequestError("pose_units must be a JSON object")
    allowed = pose_units_map()
    values: dict[str, float] = {}
    for key, value in raw_units.items():
        unit_id = str(key)
        if unit_id not in allowed:
            raise ModifierRequestError(f"unknown pose unit: {unit_id}")
        values[unit_id] = _as_unit(value, unit_id)
    return values
