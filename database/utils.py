import asyncio
import logging
import subprocess
import sys

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.sql.expression import select

from settings import Settings
from .models import Base, User

logger = logging.getLogger(__name__)


async def recreate_db(settings: Settings):
    engine = create_async_engine(settings.database_url, echo=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)


async def upgrade_database(attempts=6, delay=10) -> None:
    for _ in range(attempts):
        cmd = [sys.executable, "-m", "alembic", "upgrade", "head"]
        r = subprocess.run(cmd, capture_output=False)
        if r.returncode == 0:
            return

        logger.warning("Database is not ready!")
        await asyncio.sleep(delay)
    raise RuntimeError("Can`t upgrade database!")


async def get_user_locale(user_id: int, s: AsyncSession) -> str | None:
    user = await s.scalar(select(User).filter(User.id == user_id))
    return user.locale if user else None


async def set_user_locale(user_id: int, locale: str, s: AsyncSession):
    await s.execute(
        update(User).where(User.id == user_id).values(locale=locale)
    )
