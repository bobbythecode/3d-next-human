from service.pose_pairs import get_pose_pair, pose_pair_endpoints, pose_pairs_payload


def test_pose_pairs_catalog_has_golden_tpose_to_rest():
    payload = pose_pairs_payload()
    assert payload["version"] == "pose-pairs.v1"
    assert payload["rig"]["id"] == "mh-default"
    ids = [item["id"] for item in payload["pairs"]]
    assert "tpose-to-rest" in ids
    assert "rest-to-tpose" in ids
    assert "rest-to-left-arm-up" in ids
    assert "rest-to-torso-lean" in ids
    assert "rest-to-left-knee-bend" in ids
    assert "rest-to-kick" in ids
    pair = get_pose_pair("tpose-to-rest")
    assert pair["a"]["pose"]["id"] == "tpose"
    assert pair["b"]["pose"]["id"] == "rest"
    assert pair["duration_s"] == 1.0
    assert pair["root_policy"] == "lock_feet"
    assert pair["license"]["assets"] == "CC0-1.0"
    assert pair["name"]


def test_pose_pair_endpoints_merge_units():
    pair = get_pose_pair("rest-to-left-arm-up")
    (a_id, a_units), (b_id, b_units) = pose_pair_endpoints(pair)
    assert a_id == "rest" and a_units == {}
    assert b_id == "rest"
    assert b_units["UpperArmForwardLeft"] == 1.0
    assert b_units["UpperArmRollOutLeft"] == 0.55


def test_left_knee_bend_uses_shin_units():
    pair = get_pose_pair("rest-to-left-knee-bend")
    assert pair["version"] == "2"
    (_, _), (_, b_units) = pose_pair_endpoints(pair)
    assert "FootTurnOutLeft" in b_units
    assert "UpperLegForwardLeft" in b_units
    assert "LowerLegBendLeft1" not in b_units


def test_unknown_pose_pair_raises():
    try:
        get_pose_pair("not-a-pair")
        assert False, "expected KeyError"
    except KeyError as err:
        assert "unknown pose_pair_id" in str(err)
