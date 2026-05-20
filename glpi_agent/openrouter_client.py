from __future__ import annotations

from typing import Any

from .http_json import request_json


class OpenRouterClient:
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def chat(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> dict[str, Any]:
        return request_json(
            "POST",
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "http://localhost/glpi-agent",
                "X-Title": "GLPI LLM Agent",
            },
            payload={
                "model": self.model,
                "messages": messages,
                "tools": tools,
                "tool_choice": "auto",
            },
        )

