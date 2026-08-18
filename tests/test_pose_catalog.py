from service.pose_catalog import pose_catalog_payload


def test_pose_catalog_has_rest_and_tpose():
    payload = pose_catalog_payload()
    ids = [item["id"] for item in payload["library"]]
    assert "rest" in ids
    assert "tpose" in ids
    units = {item["id"]: item["group"] for item in payload["units"]}
    assert units.get("UpperArmUpLeft1") == "body"
    assert units.get("JawDrop") == "face"
