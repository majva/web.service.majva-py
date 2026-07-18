from logging.config import fileConfig
import os
import sys

from sqlalchemy import engine_from_config, pool

from alembic import context

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from src.infrastructure.context.sql_db.psql_dbcontext import Base
import src.infrastructure.models.profile  # noqa: F401 — register models with Base.metadata

target_metadata = Base.metadata


def _normalize_database_url(url: str) -> str:
    """Convert async driver URLs to the sync driver Alembic expects."""
    return (
        url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
        .replace("postgres+asyncpg://", "postgresql+psycopg2://")
    )


def get_database_url() -> str:
    url = os.environ.get("POSTGRES_CONNECTION_STRING")
    if url:
        return _normalize_database_url(url)

    url = config.get_main_option("sqlalchemy.url")
    if not url or url.startswith("postgresql+psycopg2://postgres:postgres@x.x.x.x"):
        raise RuntimeError(
            "Database URL is not configured. Set POSTGRES_CONNECTION_STRING "
            "or update sqlalchemy.url in alembic.ini."
        )
    return url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_database_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
