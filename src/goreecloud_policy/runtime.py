from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .engine import evaluate
from .model import Decision, PolicyRequest, PolicyRule

COMPONENT = "goreecloud-policy"
VERSION = "0.1.0-dev"


def health_payload() -> dict[str, Any]:
    return {"status": "healthy", "component": COMPONENT, "version": VERSION, "scope": "development-reference-runtime"}


def readiness_payload() -> dict[str, Any]:
    return {"status": "ready", "component": COMPONENT, "version": VERSION, "production_accepted": False}


class Handler(BaseHTTPRequestHandler):
    server_version = "GoreeCloudPolicy/0.1"

    def _json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/healthz":
            self._json(200, health_payload())
        elif self.path == "/readyz":
            self._json(200, readiness_payload())
        else:
            self._json(404, {"error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/v1/evaluate":
            self._json(404, {"error": "not_found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 262144:
                raise ValueError("request body size is invalid")
            payload = json.loads(self.rfile.read(length))
            if not isinstance(payload, dict):
                raise ValueError("payload must be an object")
            request = PolicyRequest.from_mapping(payload.get("request"))
            raw_rules = payload.get("rules", [])
            if not isinstance(raw_rules, list):
                raise ValueError("rules must be a list")
            rules = [PolicyRule.from_mapping(item) for item in raw_rules]
            result = evaluate(request, rules)
            self._json(200, result.to_dict())
        except (ValueError, json.JSONDecodeError) as exc:
            self._json(400, {"decision": Decision.ERROR.value, "error": "invalid_request", "message": str(exc)})

    def log_message(self, format: str, *args: object) -> None:
        # Do not log request bodies or policy context in the Development reference runtime.
        return


def serve() -> None:
    host = os.environ.get("GOREECLOUD_POLICY_HOST", "127.0.0.1")
    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise SystemExit("Development runtime refuses non-loopback binding")
    port = int(os.environ.get("GOREECLOUD_POLICY_PORT", "8787"))
    ThreadingHTTPServer((host, port), Handler).serve_forever()
