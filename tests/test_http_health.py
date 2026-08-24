from service.http_api import health_payload, license_payload


def test_health_names_human_api():
    payload = health_payload()
    assert payload["ok"] is True
    assert payload["service"] == "human-api"


def test_license_points_at_agpl_source():
    payload = license_payload()
    assert payload["license"] == "AGPL-3.0"
    assert payload["assets"] == "CC0-1.0"
    assert payload["output"] == "user-data"
    assert payload["code"].startswith("https://")
    assert "github.com" in payload["code"]
    assert "revision" in payload
    assert "LICENSE.md" in payload["files"]
    assert "section D" in payload["note"]
