import http.client
import threading
from http.server import ThreadingHTTPServer

import pytest

from service.http_api import HumanHttpApi


@pytest.fixture()
def server(monkeypatch):
    monkeypatch.setenv("HUMAN_API_MAX_BODY_BYTES", "1024")
    srv = ThreadingHTTPServer(("127.0.0.1", 0), HumanHttpApi)
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    yield srv.server_address[1]
    srv.shutdown()
    srv.server_close()


def test_unknown_post_path_drains_body_so_keep_alive_stays_in_sync(server):
    conn = http.client.HTTPConnection("127.0.0.1", server, timeout=5)
    conn.request("POST", "/nope", body=b'{"x": 1}', headers={"content-type": "application/json"})
    first = conn.getresponse()
    first.read()
    assert first.status == 404
    conn.request("GET", "/health")
    second = conn.getresponse()
    assert second.status == 200
    assert b'"human-api"' in second.read()


@pytest.mark.parametrize("value", ["-1", "abc", "1.5"])
def test_bad_content_length_is_rejected_not_hung(server, value):
    conn = http.client.HTTPConnection("127.0.0.1", server, timeout=3)
    conn.putrequest("POST", "/internal/humans/generate")
    conn.putheader("content-length", value)
    conn.endheaders()
    response = conn.getresponse()
    assert response.status == 400


def test_oversized_body_is_rejected(server):
    conn = http.client.HTTPConnection("127.0.0.1", server, timeout=3)
    conn.putrequest("POST", "/internal/humans/generate")
    conn.putheader("content-length", "999999")
    conn.endheaders()
    response = conn.getresponse()
    assert response.status == 413
