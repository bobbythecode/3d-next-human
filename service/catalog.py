"""Build the modelling slider catalog from MakeHuman JSON (no Qt)."""

from __future__ import annotations

import json
from collections import OrderedDict
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parents[1] / "makehuman" / "data" / "modifiers"

ETHNIC_IDS = (
    "macrodetails/African",
    "macrodetails/Asian",
    "macrodetails/Caucasian",
)

MACRO_IDS = (
    "macrodetails/Gender",
    "macrodetails/Age",
    "macrodetails-universal/Muscle",
    "macrodetails-universal/Weight",
    "macrodetails-height/Height",
    "macrodetails-proportions/BodyProportions",
) + ETHNIC_IDS

ALIAS_TO_FULLNAME = {
    "gender": "macrodetails/Gender",
    "age": "macrodetails/Age",
    "muscle": "macrodetails-universal/Muscle",
    "weight": "macrodetails-universal/Weight",
    "height": "macrodetails-height/Height",
    "proportions": "macrodetails-proportions/BodyProportions",
    "african": "macrodetails/African",
    "asian": "macrodetails/Asian",
    "caucasian": "macrodetails/Caucasian",
}

FULLNAME_TO_ALIAS = {value: key for key, value in ALIAS_TO_FULLNAME.items()}

FACE_GROUP_CATEGORY = {
    "head shape": "head",
    "head size": "head",
    "forehead": "head",
    "chin/jaw": "head",
    "left cheek": "face",
    "right cheek": "face",
    "right eye": "eyes",
    "left eye": "eyes",
    "eyebrows": "eyebrows",
    "nose size": "nose",
    "nose size details": "nose",
    "nose features": "nose",
    "mouth size": "mouth",
    "mouth size details": "mouth",
    "mouth features": "mouth",
    "right ear": "ears",
    "left ear": "ears",
    "neck": "neck",
}

ARMS_GROUP_CATEGORY = {
    "right arm": "arms",
    "left arm": "arms",
    "left shoulder": "arms",
    "right shoulder": "arms",
    "right hand": "hands",
    "left hand": "hands",
    "right leg": "legs",
    "left leg": "legs",
    "legs": "legs",
    "right foot": "feet",
    "left foot": "feet",
}

CATEGORY_LABELS = OrderedDict(
    [
        ("macro", "Macro"),
        ("head", "Head"),
        ("face", "Face"),
        ("eyes", "Eyes"),
        ("eyebrows", "Eyebrows"),
        ("nose", "Nose"),
        ("mouth", "Mouth"),
        ("ears", "Ears"),
        ("neck", "Neck"),
        ("torso", "Torso"),
        ("breasts", "Breasts"),
        ("arms", "Arms"),
        ("hands", "Hands"),
        ("legs", "Legs"),
        ("feet", "Feet"),
        ("muscle", "Muscle"),
        ("proportions", "Proportions"),
        ("body-shapes", "Body shapes"),
        ("measure", "Measure"),
    ]
)

SKIP_GROUPS = frozenset({"Genitals"})


def _load_json(name: str) -> dict[str, Any]:
    path = DATA_DIR / name
    return json.loads(path.read_text(encoding="utf-8"))


def _slider_payload(entry: dict[str, Any]) -> dict[str, Any]:
    slider_id = str(entry["mod"])
    payload: dict[str, Any] = {
        "id": slider_id,
        "label": str(entry.get("label") or slider_id.split("/")[-1]),
        "min": 0.0,
        "max": 1.0,
        "default": 0.5,
    }
    if slider_id in ETHNIC_IDS:
        payload["default"] = 1.0 / 3.0
        payload["constraint"] = "ethnic-sum-1"
    elif slider_id.startswith("macrodetails"):
        payload["default"] = 0.5
    elif "/measure-" in slider_id or slider_id.startswith("measure/"):
        payload["min"] = 0.0
        payload["max"] = 1.0
        payload["default"] = 0.5
    else:
        payload["min"] = -1.0
        payload["max"] = 1.0
        payload["default"] = 0.0
    return payload


def allowed_modifier_ids() -> frozenset[str]:
    ids: set[str] = set()
    for category in catalog_payload()["categories"]:
        for group in category["groups"]:
            for slider in group["sliders"]:
                ids.add(slider["id"])
    return frozenset(ids)


def catalog_payload() -> dict[str, Any]:
    buckets: OrderedDict[str, OrderedDict[str, list[dict[str, Any]]]] = OrderedDict(
        (key, OrderedDict()) for key in CATEGORY_LABELS
    )

    def add(category: str, group_name: str, slider: dict[str, Any]) -> None:
        groups = buckets[category]
        groups.setdefault(group_name, [])
        if any(item["id"] == slider["id"] for item in groups[group_name]):
            return
        groups[group_name].append(slider)

    modeling = _load_json("modeling_sliders.json")
    face = modeling["Face"]["modifiers"]
    for group_name, entries in face.items():
        category = FACE_GROUP_CATEGORY.get(group_name)
        if category is None:
            continue
        for entry in entries:
            add(category, group_name, _slider_payload(entry))

    for group_name, entries in modeling["Torso"]["modifiers"].items():
        for entry in entries:
            add("torso", group_name, _slider_payload(entry))

    for group_name, entries in modeling["Arms and Legs"]["modifiers"].items():
        category = ARMS_GROUP_CATEGORY.get(group_name, "arms")
        for entry in entries:
            add(category, group_name, _slider_payload(entry))

    for group_name, entries in modeling["Gender"]["modifiers"].items():
        if group_name in SKIP_GROUPS:
            continue
        for entry in entries:
            add("breasts", group_name, _slider_payload(entry))

    for entry in modeling["Macro modelling"]["modifiers"]["Macro"]:
        add("macro", "Macro", _slider_payload(entry))

    for category in buckets:
        for group_name, sliders in list(buckets[category].items()):
            for slider in sliders:
                slider_id = slider["id"]
                if "muscle" in slider_id.lower() and slider_id != "macrodetails-universal/Muscle":
                    add("muscle", group_name, slider)
                if slider_id == "macrodetails-proportions/BodyProportions" or "height" in slider_id and category == "legs":
                    add("proportions", group_name, slider)

    add("muscle", "Macro", _slider_payload({"mod": "macrodetails-universal/Muscle", "label": "Muscle"}))
    add(
        "proportions",
        "Macro",
        _slider_payload(
            {"mod": "macrodetails-proportions/BodyProportions", "label": "Proportions"}
        ),
    )

    body_shapes = _load_json("bodyshapes_sliders.json")
    for group_name, entries in body_shapes["Body shapes"]["modifiers"].items():
        for entry in entries:
            add("body-shapes", group_name, _slider_payload(entry))

    measures = _load_json("measurement_sliders.json")
    for group_name, entries in measures["Measure"]["modifiers"].items():
        for entry in entries:
            add("measure", group_name, _slider_payload(entry))

    categories = []
    for category_id, label in CATEGORY_LABELS.items():
        groups = [
            {"name": name, "sliders": sliders}
            for name, sliders in buckets[category_id].items()
            if sliders
        ]
        if not groups:
            continue
        categories.append({"id": category_id, "label": label, "groups": groups})
    return {"categories": categories}
