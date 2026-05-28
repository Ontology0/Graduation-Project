"""Load experiment YAML configs and .env variables."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).resolve().parents[2]


def project_root() -> Path:
    """Repository root (parent of ``src/``)."""
    return _PROJECT_ROOT


def resolve_path(path: str | Path) -> Path:
    """Resolve a path relative to the project root when not absolute."""
    p = Path(path)
    return p if p.is_absolute() else _PROJECT_ROOT / p


def load_env(dotenv_path: str | Path | None = None) -> None:
    """Load .env file from project root (or a custom path)."""
    path = Path(dotenv_path) if dotenv_path else _PROJECT_ROOT / ".env"
    load_dotenv(path, override=False)


def load_config(config_path: str | Path) -> dict[str, Any]:
    """Read a YAML config and return it as a dict.

    Relative paths are resolved against the project root.
    """
    path = Path(config_path)
    if not path.is_absolute():
        path = _PROJECT_ROOT / path

    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_api_key(name: str) -> str:
    """Return an environment variable or raise with a helpful message."""
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(
            f"{name} is not set. Copy .env.example to .env and fill in the value."
        )
    return value
