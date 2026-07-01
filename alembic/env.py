"""
Alembic environment configuration.

This file controls how Alembic discovers models and connects to the database.

Key decisions:
    - URL comes from backend.config.settings (not alembic.ini).
    - All ORM models are imported via backend.models so Base.metadata
      contains every table for autogenerate.
    - PostgreSQL schemas (raw, curated, analytics, platform) are created
      automatically before running migrations.
    - Uses the sync engine (psycopg2) because Alembic is synchronous.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool, text
from sqlalchemy import engine_from_config

from backend.config import settings
from backend.db.base import ALL_SCHEMAS, Base

# Import all models so Base.metadata registers every table.
import backend.models  # noqa: F401

# Alembic Config object (reads alembic.ini)
config = context.config

# Set up Python logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Override the dummy URL from alembic.ini with the real sync URL
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL_SYNC)

# Tell Alembic which metadata to compare against the database
target_metadata = Base.metadata


def include_schemas(names: set[str | None]) -> bool:
    """Filter: only include our application schemas in autogenerate."""
    # names contains schema names that Alembic found. None = public schema.
    return names is None or bool(names.intersection(ALL_SCHEMAS))


def run_migrations_offline() -> None:
    """Generate SQL scripts without a live database connection.

    Used for DBA-reviewed deployments where migrations must be
    approved before execution.

    Usage: alembic upgrade head --sql
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        version_table_schema="platform",
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against a live database.

    Creates all PostgreSQL schemas before running migrations,
    ensuring tables can be placed in their target schemas.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Create schemas if they don't exist
        for schema_name in ALL_SCHEMAS:
            connection.execute(
                text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
            )
        connection.commit()

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            version_table_schema="platform",
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
