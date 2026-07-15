"""
Alembic migration runner for local development and CI/CD pipelines.

Usage:
    python src/infrastructure/scripts/run_migrations.py --upgrade
    python src/infrastructure/scripts/run_migrations.py --autogenerate -m "add users table"
    python src/infrastructure/scripts/run_migrations.py --sync -m "add users table"
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from alembic import command
from alembic.config import Config


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _normalize_database_url(url: str) -> str:
    return (
        url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
        .replace("postgres+asyncpg://", "postgresql+psycopg2://")
    )


def _resolve_database_url() -> str:
    url = os.environ.get("POSTGRES_CONNECTION_STRING")
    if url:
        return _normalize_database_url(url)

    from src.infrastructure.utils.config_reader import ConfigReader

    config_reader = ConfigReader()
    if config_reader.is_vault_enabled():
        from src.infrastructure.context.vault.vault_service import VaultService

        vault_service = VaultService(config_reader=config_reader)
        return _normalize_database_url(vault_service.get_secret(key="POSTGRES_CONNECTION_STRING"))

    raise RuntimeError(
        "POSTGRES_CONNECTION_STRING is not set. "
        "Provide it as an environment variable, or enable Vault (vaulthc.enabled=true)."
    )


def get_alembic_config() -> Config:
    root = _project_root()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    alembic_ini = root / "src" / "infrastructure" / "alembic.ini"
    config = Config(str(alembic_ini))
    config.set_main_option("script_location", str(root / "src" / "infrastructure" / "alembic"))
    config.set_main_option("sqlalchemy.url", _resolve_database_url())
    return config


def upgrade(revision: str = "head") -> None:
    print(f"[migrate] Applying migrations up to: {revision}")
    command.upgrade(get_alembic_config(), revision)
    print("[migrate] Database is up to date.")


def autogenerate(message: str) -> None:
    if not message:
        raise ValueError("A migration message is required for --autogenerate.")

    print(f"[migrate] Generating migration: {message}")
    command.revision(get_alembic_config(), message=message, autogenerate=True)
    print("[migrate] Migration file created.")


def sync(message: str, revision: str = "head") -> None:
    autogenerate(message)
    upgrade(revision)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Alembic database migrations.")
    parser.add_argument(
        "--upgrade",
        action="store_true",
        help="Apply all pending migrations (default when no other action is passed).",
    )
    parser.add_argument(
        "--autogenerate",
        action="store_true",
        help="Generate a new migration from current SQLAlchemy models.",
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Autogenerate a migration and then apply it in one step.",
    )
    parser.add_argument(
        "-m",
        "--message",
        default="",
        help="Migration message (required for --autogenerate and --sync).",
    )
    parser.add_argument(
        "--revision",
        default="head",
        help="Target revision for --upgrade (default: head).",
    )

    args = parser.parse_args()

    if args.sync:
        sync(args.message, args.revision)
        return

    if args.autogenerate:
        autogenerate(args.message)
        return

    if args.upgrade or not any([args.autogenerate, args.sync]):
        upgrade(args.revision)


if __name__ == "__main__":
    main()
