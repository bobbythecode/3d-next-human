import pytest

from service.bootstrap import qt_imported
from service.session import generate


@pytest.mark.integration
def test_generate_obj_metres_without_qt():
    result = generate({"gender": 0.5, "age": 0.5, "height": 0.5, "weight": 0.5, "muscle": 0.5})
    assert result["unit"] == "m"
    assert result["up"] == "y"
    assert result["height_cm"] > 100
    assert result["height_cm"] < 220
    assert "\nv " in result["obj"] or result["obj"].startswith("v ") or "v " in result["obj"]
    faces = [line for line in result["obj"].splitlines() if line.startswith("f ")]
    verts = [line for line in result["obj"].splitlines() if line.startswith("v ")]
    assert len(verts) > 1000
    assert len(faces) > 1000
    sample = verts[100].split()
    y = float(sample[2])
    assert y < 3.0
    ys = [float(line.split()[2]) for line in verts]
    assert min(ys) == pytest.approx(0.0, abs=0.02)
    assert max(ys) == pytest.approx(result["height_cm"] / 100.0, abs=0.08)
    assert result["applied"]["gender"] == 0.5
    assert qt_imported() is False


@pytest.mark.integration
def test_generate_applies_height_cm_and_gender():
    short = generate({"height_cm": 150, "gender": 0.0, "age": 0.5, "weight": 0.5, "muscle": 0.5})
    tall = generate({"height_cm": 180, "gender": 1.0, "age": 0.5, "weight": 0.5, "muscle": 0.5})
    assert short["applied"]["height_cm"] == 150.0
    assert short["applied"]["gender"] == 0.0
    assert tall["applied"]["height_cm"] == 180.0
    assert tall["applied"]["gender"] == 1.0
    assert abs(short["height_cm"] - 150.0) < 8.0
    assert abs(tall["height_cm"] - 180.0) < 8.0
    assert tall["height_cm"] > short["height_cm"] + 15.0
    assert qt_imported() is False


@pytest.mark.integration
def test_generate_rejects_unknown_modifier():
    from service.modifier_request import ModifierRequestError

    with pytest.raises(ModifierRequestError, match="unknown modifier"):
        generate({"modifiers": {"not-a-real-slider": 0.5}})


@pytest.mark.integration
def test_generate_applies_head_and_torso_modifiers():
    baseline = generate({"gender": 0.5, "age": 0.5, "weight": 0.5, "muscle": 0.5, "height": 0.5})
    shaped = generate(
        {
            "gender": 0.5,
            "age": 0.5,
            "weight": 0.5,
            "muscle": 0.5,
            "height": 0.5,
            "modifiers": {
                "eyes/r-eye-scale-decr|incr": 0.8,
                "torso/torso-scale-horiz-decr|incr": 0.7,
            },
        }
    )
    assert shaped["obj"] != baseline["obj"]
    assert qt_imported() is False


@pytest.mark.integration
def test_generate_applies_tpose_differently_from_rest():
    rest = generate({"pose": {"id": "rest"}})
    tpose = generate({"pose": {"id": "tpose"}})
    assert rest["pose"]["id"] == "rest"
    assert tpose["pose"]["id"] == "tpose"
    assert tpose["obj"] != rest["obj"]

