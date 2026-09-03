from service.pose_pairs import get_pose_pair, main, pose_pair_endpoints, pose_pairs_payload


def test_pose_pairs_catalog_lists_visible_pairs():
    payload = pose_pairs_payload()
    assert payload["version"] == "pose-pairs.v1"
    assert payload["rig"]["id"] == "mh-default"
    ids = [item["id"] for item in payload["pairs"]]
    assert "tpose-to-rest" in ids
    assert "tpose-to-left-arm-down" in ids
    assert "tpose-to-torso-lean" in ids
    assert "tpose-to-left-knee-bend" in ids
    assert "tpose-to-left-kick" in ids
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
    (a_id, a_units, a_from, a_bones), (b_id, b_units, b_from, b_bones) = (
        pose_pair_endpoints(pair)
    )
    assert a_id == "rest" and a_units == {} and a_from is None and a_bones == ()
    assert b_id == "rest" and b_from is None and b_bones == ()
    assert b_units["UpperArmForwardLeft"] == 1.0
    assert b_units["UpperArmRollOutLeft"] == 0.55


def test_tpose_to_left_arm_down_replaces_left_arm_from_rest():
    pair = get_pose_pair("tpose-to-left-arm-down")
    assert pair["version"] == "2"
    (a_id, a_units, a_from, a_bones), (b_id, b_units, b_from, b_bones) = (
        pose_pair_endpoints(pair)
    )
    assert a_id == "tpose" and a_units == {} and a_from is None
    assert b_id == "tpose" and b_units == {}
    assert b_from == "rest"
    assert "upperarm01.L" in b_bones
    assert "wrist.L" in b_bones
    assert "UpperArmDownLeft" not in (pair["b"]["pose"].get("units") or {})


def test_tpose_to_torso_lean_uses_torso_unit_on_tpose():
    pair = get_pose_pair("tpose-to-torso-lean")
    (a_id, a_units, a_from, _), (b_id, b_units, b_from, _) = pose_pair_endpoints(
        pair
    )
    assert a_id == "tpose" and a_units == {} and a_from is None
    assert b_id == "tpose" and b_from is None
    assert b_units["TorsoLeft"] == 0.9


def test_tpose_to_left_knee_bend_uses_shin_units_on_tpose():
    pair = get_pose_pair("tpose-to-left-knee-bend")
    (a_id, a_units, a_from, _), (b_id, b_units, b_from, _) = pose_pair_endpoints(
        pair
    )
    assert a_id == "tpose" and a_units == {} and a_from is None
    assert b_id == "tpose" and b_from is None
    assert b_units["UpperLegForwardLeft"] == 0.7
    assert b_units["FootTurnOutLeft"] == 0.55


def test_tpose_to_left_kick_uses_kick_bvh():
    pair = get_pose_pair("tpose-to-left-kick")
    assert pair["version"] == "2"
    (a_id, a_units, _, _), (b_id, b_units, b_from, b_bones) = pose_pair_endpoints(
        pair
    )
    assert a_id == "tpose" and a_units == {}
    assert b_id == "kick" and b_units == {}
    assert b_from == "tpose"
    assert "upperarm01.L" in b_bones
    assert "upperarm01.R" in b_bones


def test_left_knee_bend_uses_shin_units():
    pair = get_pose_pair("rest-to-left-knee-bend")
    assert pair["version"] == "2"
    (_, _, _, _), (_, b_units, _, _) = pose_pair_endpoints(pair)
    assert "FootTurnOutLeft" in b_units
    assert "UpperLegForwardLeft" in b_units
    assert "LowerLegBendLeft1" not in b_units


def test_rest_to_kick_uses_library_bvh():
    pair = get_pose_pair("rest-to-kick")
    (a_id, a_units, _, _), (b_id, b_units, _, _) = pose_pair_endpoints(pair)
    assert a_id == "rest" and a_units == {}
    assert b_id == "kick" and b_units == {}


def test_unknown_pose_pair_raises():
    try:
        get_pose_pair("not-a-pair")
        assert False, "expected KeyError"
    except KeyError as err:
        assert "unknown pose_pair_id" in str(err)


def test_main_dumps_catalog_and_pair():
    import io
    import json
    from contextlib import redirect_stdout

    catalog_buf = io.StringIO()
    with redirect_stdout(catalog_buf):
        assert main([]) == 0
    catalog = json.loads(catalog_buf.getvalue())
    assert catalog["version"] == "pose-pairs.v1"
    ids = [item["id"] for item in catalog["pairs"]]
    assert "rest-to-kick" in ids

    pair_buf = io.StringIO()
    with redirect_stdout(pair_buf):
        assert main(["rest-to-kick"]) == 0
    pair = json.loads(pair_buf.getvalue())
    assert pair["id"] == "rest-to-kick"
    assert pair["b"]["pose"]["id"] == "kick"

    assert main(["not-a-pair"]) == 1
