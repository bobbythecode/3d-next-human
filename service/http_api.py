"""Headless HTTP facade for human-api (AGPL process)."""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

from .modifier_request import ModifierRequestError

SERVICE = "human-api"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8001

logger = logging.getLogger(SERVICE)


def _configure_logging() -> None:
    level = os.environ.get("LOG_LEVEL", "info").strip().lower()
    numeric = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(level=numeric, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")

def _license_body() -> dict[str, Any]:
    code_url = os.environ.get(
        "HUMAN_API_GIT_URL",
        "https://github.com/bobbythecode/3d-next-human",
    )
    revision = os.environ.get("HUMAN_API_GIT_SHA", "unknown")
    return {
        "license": "AGPL-3.0",
        "code": code_url,
        "revision": revision,
        "assets": "CC0-1.0",
        "output": "user-data",
        "files": [
            "LICENSE.md",
            "LICENSE.CODE.md",
            "LICENSE.ASSETS.md",
            "documents/guides/license.md",
        ],
        "note": (
            "Source of this network service is this repository "
            "(MakeHuman + service/ facade), AGPL-3.0. Bundled assets are CC0. "
            "Exported OBJ is user data (LICENSE.md section D). "
            "AGPL §13 corresponding source: see `code` URL, `revision`, and LICENSE files."
        ),
    }


def health_payload() -> dict[str, Any]:
    return {"ok": True, "service": SERVICE}


def license_payload() -> dict[str, Any]:
    return _license_body()


class HumanHttpApi(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, format, *args):  # noqa: A003
        logger.info("%s - %s", self.address_string(), format % args)

    def _request_id(self) -> str:
        raw = self.headers.get("x-request-id", "").strip()
        return raw or str(uuid.uuid4())

    def _dispatch(self, handler):  # type: ignore[no-untyped-def]
        request_id = self._request_id()
        path = urlparse(self.path).path
        started = time.perf_counter()
        logger.info("enter %s %s requestId=%s", self.command, path, request_id)
        try:
            handler()
            status = getattr(self, "_last_status", 200)
        except Exception as err:  # noqa: BLE001
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            logger.exception(
                "exit %s %s status=500 elapsedMs=%s requestId=%s",
                self.command,
                path,
                elapsed_ms,
                request_id,
            )
            self._send_json(500, {"ok": False, "error": str(err)[:512]})
            return
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        log = logger.warning if status >= 400 else logger.info
        log(
            "exit %s %s status=%s elapsedMs=%s requestId=%s",
            self.command,
            path,
            status,
            elapsed_ms,
            request_id,
        )

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        self._last_status = status
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "application/json; charset=utf-8")
        self.send_header("content-length", str(len(body)))
        self.send_header("x-request-id", self._request_id())
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        def handler() -> None:
            path = urlparse(self.path).path
            if path == "/health":
                self._send_json(200, health_payload())
                return
            if path == "/license":
                self._send_json(200, license_payload())
                return
            if path == "/internal/humans/modifiers":
                from .catalog import catalog_payload

                self._send_json(200, catalog_payload())
                return
            if path == "/internal/humans/poses":
                from .pose_catalog import pose_catalog_payload

                self._send_json(200, pose_catalog_payload())
                return
            if path == "/internal/humans/pose-pairs":
                from .pose_pairs import pose_pairs_payload

                self._send_json(200, pose_pairs_payload())
                return
            self._send_json(404, {"ok": False, "error": "not found"})

        self._dispatch(handler)

    def do_POST(self) -> None:  # noqa: N802
        def handler() -> None:
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

        self._dispatch(handler)


def serve(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    httpd = ThreadingHTTPServer((host, port), HumanHttpApi)
    print(f"human-api listening on http://{host}:{port}", flush=True)
    httpd.serve_forever()


def main() -> None:
    _configure_logging()
    host = os.environ.get("HUMAN_API_HOST", DEFAULT_HOST)
    port = int(os.environ.get("HUMAN_API_PORT", str(DEFAULT_PORT)))
    serve(host, port)


if __name__ == "__main__":
    main()
