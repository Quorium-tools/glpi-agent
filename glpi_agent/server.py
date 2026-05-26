from __future__ import annotations

import json
import os
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .config import Settings
from .glpi_client import GlpiClient
from .openrouter_client import OpenRouterClient


def _agent_type() -> str:
    return os.getenv("GLPI_AGENT_TYPE", "admin").strip().lower()


def run_agent(message: str, model: str | None = None) -> str:
    agent_type = _agent_type()

    if os.getenv("GLPI_AGENT_DEV_SUBPROCESS", "").strip().lower() in {"1", "true", "yes", "on"}:
        args = [sys.executable, "-m", "glpi_agent.cli_knowledge_base_agent" if agent_type == "knowledge-base" else "glpi_agent.cli"]
        if model:
            args.extend(["--model", model])
        args.append(message)

        completed = subprocess.run(args, check=False, capture_output=True, text=True, timeout=120)
        if completed.returncode != 0:
            detail = completed.stderr.strip() or completed.stdout.strip() or f"exit code {completed.returncode}"
            raise RuntimeError(detail)
        return completed.stdout

    settings = Settings.from_env()
    if model:
        settings = replace(settings, openrouter_model=model)

    llm = OpenRouterClient(settings.openrouter_api_key, settings.openrouter_model)
    with GlpiClient(settings) as glpi:
        if agent_type == "knowledge-base":
            from .knowledge_base_agent import KbAgent
            return KbAgent(llm, glpi).run(message)
        from .agent import GlpiAgent
        return GlpiAgent(llm, glpi).run(message)


class GlpiAgentHandler(BaseHTTPRequestHandler):
    server_version = "GlpiAgentHTTP/1.0"

    def do_GET(self) -> None:
        if self.path == "/health":
            self._send_json({"status": "ok", "agent": _agent_type()})
            return
        self._send_json({"error": "Not found."}, status=404)

    def do_POST(self) -> None:
        if self.path != "/chat":
            self._send_json({"error": "Not found."}, status=404)
            return

        try:
            payload = self._read_json()
            message = str(payload.get("message", "")).strip()
            if not message:
                self._send_json({"error": "Message is required."}, status=400)
                return

            model = str(payload.get("model", "")).strip() or None
            answer = run_agent(message, model=model)
            self._send_json({"answer": answer.strip() or "The agent finished without a text response."})
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON request."}, status=400)
        except Exception as exc:
            self._send_json({"error": "The agent failed.", "detail": str(exc)}, status=500)

    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"{self.address_string()} - {fmt % args}")

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        if not body:
            return {}
        data = json.loads(body.decode("utf-8"))
        if not isinstance(data, dict):
            raise json.JSONDecodeError("JSON body must be an object", body.decode("utf-8"), 0)
        return data

    def _send_json(self, payload: dict[str, Any], status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    host = os.getenv("GLPI_AGENT_HOST", "0.0.0.0")
    port = int(os.getenv("GLPI_AGENT_PORT", "8000"))
    agent_type = _agent_type()
    server = ThreadingHTTPServer((host, port), GlpiAgentHandler)
    print(f"GLPI agent backend [{agent_type}] listening on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
