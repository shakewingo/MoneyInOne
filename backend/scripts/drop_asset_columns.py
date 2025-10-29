#!/usr/bin/env python3
"""One-off migration script to drop deprecated columns from assets.

Removes columns: original_amount, current_amount from the `assets` table.

Supported backends:
- SQLite (requires SQLite >= 3.35 for ALTER TABLE DROP COLUMN)
- PostgreSQL

Usage:
    python backend/scripts/drop_asset_columns.py

Notes:
- This script is idempotent: it checks for column existence before attempting to drop.
- Rollback strategy: restore from DB backup. Re-adding columns is not supported here.
"""

import asyncio
import logging
from typing import List
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

from app.core.config import settings

logger = logging.getLogger(__name__)


ASSET_TABLE = "assets"
DEPRECATED_COLUMNS: List[str] = ["original_amount", "current_amount"]


async def drop_columns_sqlite(engine) -> None:
    """Drop columns for SQLite (if supported by version)."""
    async with engine.begin() as conn:
        # Discover existing columns
        result = await conn.execute(text(f"PRAGMA table_info({ASSET_TABLE})"))
        existing_cols = {row[1] for row in result.fetchall()}  # row[1] = name

        for col in DEPRECATED_COLUMNS:
            if col in existing_cols:
                logger.info(f"Dropping column '{col}' from {ASSET_TABLE} (SQLite)...")
                # Requires SQLite 3.35+: ALTER TABLE table DROP COLUMN column-name
                try:
                    await conn.execute(text(f"ALTER TABLE {ASSET_TABLE} DROP COLUMN {col}"))
                except Exception as e:
                    raise RuntimeError(
                        "SQLite engine does not support DROP COLUMN. "
                        "Upgrade SQLite to >= 3.35 or perform manual migration."
                    ) from e


async def drop_columns_postgres(engine) -> None:
    """Drop columns for PostgreSQL using IF EXISTS."""
    async with engine.begin() as conn:
        for col in DEPRECATED_COLUMNS:
            logger.info(f"Dropping column '{col}' from {ASSET_TABLE} (PostgreSQL) if exists...")
            await conn.execute(
                text(f"ALTER TABLE {ASSET_TABLE} DROP COLUMN IF EXISTS {col}")
            )


async def main() -> int:
    logging.basicConfig(level=logging.INFO)
    engine = create_async_engine(settings.database_url, echo=True)

    try:
        dialect = engine.url.get_backend_name()
        logger.info(f"Connected using dialect: {dialect}")

        if "sqlite" in dialect:
            await drop_columns_sqlite(engine)
        elif "postgresql" in dialect:
            await drop_columns_postgres(engine)
        else:
            raise RuntimeError(f"Unsupported dialect for this script: {dialect}")

        logger.info("Completed dropping deprecated asset columns.")
        return 0
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return 1
    finally:
        await engine.dispose()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))


