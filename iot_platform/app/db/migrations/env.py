from __future__ import with_statement

import os
import sys
from pathlib import Path
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.db.base import Base
import app.models.user  # noqa: F401
import app.models.device  # noqa: F401
import app.models.telemetry  # noqa: F401

config = context.config
fileConfig(config.config_file_name)

# Prefer explicit DATABASE_URL. If not provided, build it from POSTGRES_* vars
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    pg_host = os.environ.get("POSTGRES_HOST", "localhost")
    pg_port = os.environ.get("POSTGRES_PORT", "5432")
    pg_db = os.environ.get("POSTGRES_DB", "iot_platform")
    pg_user = os.environ.get("POSTGRES_USER", "iot_user")
    pg_password = os.environ.get("POSTGRES_PASSWORD", "")
    if pg_password:
        database_url = f"postgresql+psycopg2://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"
    else:
        # If no password provided, build URL without it (useful for local setups with trust auth)
        database_url = f"postgresql+psycopg2://{pg_user}@{pg_host}:{pg_port}/{pg_db}"

config.set_main_option("sqlalchemy.url", database_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
