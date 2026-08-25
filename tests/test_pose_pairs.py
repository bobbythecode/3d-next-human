from service.pose_pairs import get_pose_pair, pose_pairs_payload


def test_pose_pairs_catalog_has_golden_tpose_to_rest():
    payload = pose_pairs_payload()
    assert payload["version"] == "pose-pairs.v1"
    assert payload["rig"]["id"] == "mh-default"
    ids = [item["id"] for item in payload["pairs"]]
    assert "tpose-to-rest" in ids
    pair = get_pose_pair("tpose-to-rest")
    assert pair["a"]["pose"]["id"] == "tpose"
    assert pair["b"]["pose"]["id"] == "rest"
    assert pair["duration_s"] == 1.0
    assert pair["root_policy"] == "lock_feet"
    assert pair["license"]["assets"] == "CC0-1.0"


def test_unknown_pose_pair_raises():
    try:
        get_pose_pair("not-a-pair")
        assert False, "expected KeyError"
    except KeyError as err:
        assert "unknown pose_pair_id" in str(err)
