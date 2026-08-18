from service.catalog import catalog_payload


def test_catalog_lists_macro_and_body_categories():
    payload = catalog_payload()
    labels = [item["label"] for item in payload["categories"]]
    for name in (
        "Macro",
        "Head",
        "Face",
        "Eyes",
        "Eyebrows",
        "Nose",
        "Mouth",
        "Ears",
        "Neck",
        "Torso",
        "Breasts",
        "Arms",
        "Hands",
        "Legs",
        "Feet",
        "Muscle",
        "Proportions",
    ):
        assert name in labels
    assert "Pose" not in labels
    assert "Skin" not in labels
    macro = next(item for item in payload["categories"] if item["id"] == "macro")
    slider_ids = [slider["id"] for group in macro["groups"] for slider in group["sliders"]]
    for required in (
        "macrodetails/Gender",
        "macrodetails/Age",
        "macrodetails-universal/Muscle",
        "macrodetails-universal/Weight",
        "macrodetails-height/Height",
        "macrodetails-proportions/BodyProportions",
        "macrodetails/African",
        "macrodetails/Asian",
        "macrodetails/Caucasian",
    ):
        assert required in slider_ids
    ethnic = next(s for s in macro["groups"][0]["sliders"] if s["id"] == "macrodetails/African")
    assert ethnic["constraint"] == "ethnic-sum-1"
