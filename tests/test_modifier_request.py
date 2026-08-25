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
    applied = HumanModifierRequest.parse({"height_cm": 160, "gender": 1}).as_dict()
    assert applied["gender"] == 1.0
    assert applied["height_cm"] == 160.0
    assert applied["proportions"] == 0.5
    assert "height" not in applied


def test_accepts_body_cm_measures():
    req = HumanModifierRequest.parse(
        {
            "height_cm": 165,
            "body": {
                "bust": 90,
                "waist": 70,
                "hips": 95,
                "bust_line": 25,
                "arm_pose_angle": 45,
                "leg_circ": 55,
            },
        }
    )
    assert req.height_cm == 165.0
    assert req.body_cm == {
        "bust": 90.0,
        "waist": 70.0,
        "hips": 95.0,
        "bust_line": 25.0,
        "arm_pose_angle": 45.0,
        "leg_circ": 55.0,
    }
    applied = req.as_dict()
    assert applied["body"]["bust"] == 90.0
    assert applied["body"]["bust_line"] == 25.0
    assert applied["body"]["arm_pose_angle"] == 45.0


def test_body_height_promotes_to_height_cm():
    req = HumanModifierRequest.parse({"body": {"height": 160, "bust": 88}})
    assert req.height_cm == 160.0
    assert req.body_cm["height"] == 160.0


def test_rejects_invalid_body_cm():
    with pytest.raises(ModifierRequestError, match="body.bust"):
        HumanModifierRequest.parse({"body": {"bust": -1}})
    with pytest.raises(ModifierRequestError, match="JSON object"):
        HumanModifierRequest.parse({"body": []})


def test_accepts_fullname_modifiers_and_proportions():
    req = HumanModifierRequest.parse(
        {
            "proportions": 0.8,
            "modifiers": {"macrodetails-proportions/BodyProportions": 0.9},
        }
    )
    values = req.modifier_values()
    assert values["macrodetails-proportions/BodyProportions"] == 0.9
    with pytest.raises(ModifierRequestError, match="unknown modifier"):
        HumanModifierRequest.parse({"modifiers": {"not-a-real-slider": 0.5}})


def test_ethnicity_values_sum_to_one():
    values = HumanModifierRequest.parse(
        {"african": 1, "asian": 1, "caucasian": 1}
    ).modifier_values()
    ethnic = [values["macrodetails/African"], values["macrodetails/Asian"], values["macrodetails/Caucasian"]]
    assert sum(ethnic) == pytest.approx(1.0)


def test_accepts_pose_and_pose_units():
    req = HumanModifierRequest.parse(
        {"pose": {"id": "tpose"}, "pose_units": {"UpperArmUpLeft1": 0.3}}
    )
    assert req.pose_id == "tpose"
    assert req.pose_units["UpperArmUpLeft1"] == 0.3


def test_rejects_unknown_pose_and_pose_unit():
    with pytest.raises(ModifierRequestError, match="unknown pose id"):
        HumanModifierRequest.parse({"pose": {"id": "no-such-pose"}})
    with pytest.raises(ModifierRequestError, match="unknown pose unit"):
        HumanModifierRequest.parse({"pose_units": {"NoSuchUnit": 0.5}})


def test_include_rig_defaults_pose_pair():
    req = HumanModifierRequest.parse({"include_rig": True})
    assert req.include_rig is True
    assert req.pose_pair_id == "tpose-to-rest"


def test_pose_pair_requires_include_rig():
    with pytest.raises(ModifierRequestError, match="include_rig"):
        HumanModifierRequest.parse({"pose_pair_id": "tpose-to-rest"})


def test_rejects_unknown_pose_pair():
    with pytest.raises(ModifierRequestError, match="unknown pose_pair_id"):
        HumanModifierRequest.parse({"include_rig": True, "pose_pair_id": "nope"})
