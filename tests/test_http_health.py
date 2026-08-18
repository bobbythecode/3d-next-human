from service.http_api import health_payload


def test_health_names_human_api():
    payload = health_payload()
    assert payload["ok"] is True
    assert payload["service"] == "human-api"
