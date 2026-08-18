"""Parse MakeHuman macro sliders for human-api generate."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional

MACRO_KEYS = ("gender", "age", "weight", "muscle")
HEIGHT_KEYS = ("height", "height_cm")
ALLOWED_KEYS = frozenset(MACRO_KEYS + HEIGHT_KEYS)


class ModifierRequestError(ValueError):
    pass


def _as_unit(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ModifierRequestError(f"{name} must be a number")
    number = float(value)
    if number < 0.0 or number > 1.0:
        raise ModifierRequestError(f"{name} must be between 0 and 1")
    return number


def _as_cm(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ModifierRequestError("height_cm must be a number")
    number = float(value)
    if number <= 0.0 or number > 250.0:
        raise ModifierRequestError("height_cm must be in (0, 250]")
    return number


@dataclass(frozen=True)
class HumanModifierRequest:
    gender: float = 0.5
    age: float = 0.5
    weight: float = 0.5
    muscle: float = 0.5
    height: Optional[float] = 0.5
    height_cm: Optional[float] = None

    @classmethod
    def parse(cls, payload: object) -> "HumanModifierRequest":
        if payload is None:
            payload = {}
        if not isinstance(payload, Mapping):
            raise ModifierRequestError("body must be a JSON object")
        unknown = [key for key in payload.keys() if key not in ALLOWED_KEYS]
        if unknown:
            raise ModifierRequestError(
                "unknown fields: " + ", ".join(sorted(str(k) for k in unknown))
            )
        if "height" in payload and "height_cm" in payload:
            raise ModifierRequestError("send height or height_cm, not both")

        values = {key: _as_unit(payload[key], key) for key in MACRO_KEYS if key in payload}
        height: Optional[float] = 0.5
        height_cm: Optional[float] = None
        if "height_cm" in payload:
            height = None
            height_cm = _as_cm(payload["height_cm"])
        elif "height" in payload:
            height = _as_unit(payload["height"], "height")
        return cls(height=height, height_cm=height_cm, **values)

    def as_dict(self) -> dict[str, float]:
        payload: dict[str, float] = {
            "gender": self.gender,
            "age": self.age,
            "weight": self.weight,
            "muscle": self.muscle,
        }
        if self.height_cm is not None:
            payload["height_cm"] = self.height_cm
        else:
            payload["height"] = float(self.height if self.height is not None else 0.5)
        return payload
