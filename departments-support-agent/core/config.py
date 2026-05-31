from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def load_dotenv(path: str = ".env") -> None:
    env_path = Path(path)
    if not env_path.exists():
        return

    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    openrouter_api_key: str
    openrouter_model: str
    GLPI_BASE_URL: str
    glpi_api_version: str
    glpi_oauth_client_id: str | None
    glpi_oauth_client_secret: str | None
    glpi_oauth_scope: str
    glpi_username: str | None
    glpi_password: str | None
    dry_run: bool

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        settings = cls(
            openrouter_api_key=os.getenv("OPENROUTER_API_KEY", ""),
            openrouter_model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
            GLPI_BASE_URL=os.getenv("GLPI_BASE_URL", "").rstrip("/"),
            glpi_api_version=os.getenv("GLPI_API_VERSION", "v2.3").strip("/"),
            glpi_oauth_client_id=os.getenv("GLPI_OAUTH_CLIENT_ID") or None,
            glpi_oauth_client_secret=os.getenv("GLPI_OAUTH_CLIENT_SECRET") or None,
            glpi_oauth_scope=os.getenv("GLPI_OAUTH_SCOPE", "api"),
            glpi_username=os.getenv("GLPI_USERNAME") or None,
            glpi_password=os.getenv("GLPI_PASSWORD") or None,
            dry_run=_truthy(os.getenv("GLPI_AGENT_DRY_RUN")),
        )
        settings.validate()
        return settings

    def validate(self) -> None:
        missing = []
        if not self.openrouter_api_key:
            missing.append("OPENROUTER_API_KEY")
        if not self.GLPI_BASE_URL:
            missing.append("GLPI_BASE_URL")
        if missing:
            raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

        if not self.glpi_api_version.startswith("v2"):
            raise RuntimeError("This project is configured for GLPI API V2. Set GLPI_API_VERSION=v2 or v2.3.")

        has_oauth_client = bool(self.glpi_oauth_client_id and self.glpi_oauth_client_secret)
        has_password_grant = bool(self.glpi_username and self.glpi_password)
        if not has_oauth_client or not has_password_grant:
            raise RuntimeError(
                "Set GLPI_OAUTH_CLIENT_ID, GLPI_OAUTH_CLIENT_SECRET, GLPI_USERNAME, and "
                "GLPI_PASSWORD for GLPI V2 OAuth password grant auth."
            )
