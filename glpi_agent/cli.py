from __future__ import annotations

import argparse
from dataclasses import replace

from .agent import GlpiAgent
from .config import Settings
from .glpi_client import GlpiClient
from .openrouter_client import OpenRouterClient


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="OpenRouter-powered GLPI agent")
    parser.add_argument("--dry-run", action="store_true", help="Preview GLPI write operations without sending them")
    parser.add_argument("--model", help="Override OPENROUTER_MODEL for this run")
    parser.add_argument("--show-config", action="store_true", help="Print the active non-secret configuration and exit")
    parser.add_argument("prompt", nargs="*", help="One-shot instruction for the agent")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    settings = Settings.from_env()
    if args.dry_run:
        settings = replace(settings, dry_run=True)
    if args.model:
        settings = replace(settings, openrouter_model=args.model)

    if args.show_config:
        print(f"OpenRouter model: {settings.openrouter_model}")
        print(f"GLPI base URL: {settings.glpi_base_url}")
        print(f"GLPI API version: {settings.glpi_api_version}")
        print(f"GLPI OAuth scope: {settings.glpi_oauth_scope}")
        print(f"Dry run: {settings.dry_run}")
        return

    llm = OpenRouterClient(settings.openrouter_api_key, settings.openrouter_model)

    with GlpiClient(settings) as glpi:
        agent = GlpiAgent(llm, glpi)
        if args.prompt:
            print(agent.run(" ".join(args.prompt)))
            return

        print("GLPI agent ready. Type 'exit' to quit.")
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
