from __future__ import annotations

import argparse
import sys
from dataclasses import replace

from .knowledge_base_agent import KbAgent
from .config import Settings
from .glpi_client import GlpiClient
from .openrouter_client import OpenRouterClient


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Knowledge Base Agent for non-IT departments")
    parser.add_argument("--model", help="Override OPENROUTER_MODEL for this run")
    parser.add_argument("--show-config", action="store_true", help="Print the active non-secret configuration and exit")
    parser.add_argument("prompt", nargs="*", help="One-shot question or issue")
    return parser


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = build_parser().parse_args()
    settings = Settings.from_env()
    if args.model:
        settings = replace(settings, openrouter_model=args.model)

    if args.show_config:
        print(f"OpenRouter model: {settings.openrouter_model}")
        print(f"GLPI base URL: {settings.glpi_base_url}")
        print(f"GLPI API version: {settings.glpi_api_version}")
        print(f"Target: Non-IT departments only")
        return

    llm = OpenRouterClient(settings.openrouter_api_key, settings.openrouter_model)

    with GlpiClient(settings) as glpi:
        agent = KbAgent(llm, glpi)
        if args.prompt:
            print(agent.run(" ".join(args.prompt)))
            return

        print("Knowledge Base Agent ready. Type 'exit' to quit.")
        while True:
            try:
                prompt = input("> ").strip()
            except EOFError:
                break
            if prompt.lower() in {"exit", "quit"}:
                break
            if prompt:
                print(agent.run(prompt))


if __name__ == "__main__":
    main()
