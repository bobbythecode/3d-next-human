import pytest

from service.modifier_request import HumanModifierRequest, ModifierRequestError


def test_defaults_when_body_empty():
    req = HumanModifierRequest.parse({})
    assert req.gender == 0.5
    assert req.age == 0.5
    assert req.weight == 0.5
    assert req.muscle == 0.5
    assert req.height == 0.5
    assert req.height_cm is None


def test_unit_macros_and_height_slider():
    req = HumanModifierRequest.parse(
        {"gender": 1, "age": 0.2, "height": 0.8, "weight": 0.4, "muscle": 0.6}
    )
    assert req.gender == 1.0
    assert req.height == 0.8
    assert req.height_cm is None


def test_height_cm_exclusive():
    req = HumanModifierRequest.parse({"height_cm": 150})
    assert req.height is None
    assert req.height_cm == 150.0
    with pytest.raises(ModifierRequestError, match="not both"):
        HumanModifierRequest.parse({"height": 0.5, "height_cm": 150})


def test_rejects_out_of_range_and_unknown():
    with pytest.raises(ModifierRequestError, match="between 0 and 1"):
        HumanModifierRequest.parse({"gender": 1.2})
    with pytest.raises(ModifierRequestError, match="unknown"):
        HumanModifierRequest.parse({"bust": 90})
    with pytest.raises(ModifierRequestError, match="JSON object"):
        HumanModifierRequest.parse([])


def test_as_dict_echoes_height_cm():
    assert HumanModifierRequest.parse({"height_cm": 160, "gender": 1}).as_dict() == {
        "gender": 1.0,
        "age": 0.5,
        "weight": 0.5,
        "muscle": 0.5,
        "height_cm": 160.0,
    }
