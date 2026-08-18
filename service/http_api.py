"""Headless HTTP facade for human-api (AGPL process)."""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

from .modifier_request import ModifierRequestError

SERVICE = "human-api"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8001

LICENSE_BODY = {
    "license": "AGPL-3.0",
    "code": "https://github.com/bobbythecode/3d-next-human",
    "note": "Source of this network service is the 3d-next-human repository. Exported OBJ is user data (LICENSE.md section D).",
}


def health_payload() -> dict[str, Any]:
    return {"ok": True, "service": SERVICE}


class HumanHttpApi(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, format, *args):
        return None

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "application/json; charset=utf-8")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/health":
            self._send_json(200, health_payload())
            return
        if path == "/license":
            self._send_json(200, LICENSE_BODY)
            return
        if path == "/internal/humans/modifiers":
            from .catalog import catalog_payload

            self._send_json(200, catalog_payload())
            return
        if path == "/internal/humans/poses":
            from .pose_catalog import pose_catalog_payload

            self._send_json(200, pose_catalog_payload())
            return
        self._send_json(404, {"ok": False, "error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path != "/internal/humans/generate":
            self._send_json(404, {"ok": False, "error": "not found"})
            return
        length = int(self.headers.get("content-length") or "0")
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._send_json(400, {"ok": False, "error": "body must be JSON"})
            return
        from .session import generate

        try:
            result = generate(payload)
        except ModifierRequestError as err:
            self._send_json(400, {"ok": False, "error": str(err)})
            return
        except Exception as err:  # noqa: BLE001
            self._send_json(500, {"ok": False, "error": str(err)})
            return
        self._send_json(200, result)


def serve(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    httpd = ThreadingHTTPServer((host, port), HumanHttpApi)
    print(f"human-api listening on http://{host}:{port}", flush=True)
    httpd.serve_forever()


def main() -> None:
    host = os.environ.get("HUMAN_API_HOST", DEFAULT_HOST)
    port = int(os.environ.get("HUMAN_API_PORT", str(DEFAULT_PORT)))
    serve(host, port)


if __name__ == "__main__":
    main()
