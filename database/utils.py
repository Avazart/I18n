import asyncio
import logging
import subprocess
import sys

from sqlalchemy import Result
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.sql.expression import (
    select
)

from .models import Base, Lang, User
from settings import Settings

logger = logging.getLogger(__name__)


async def recreate_db(settings: Settings):
    engine = create_async_engine(settings.database_url, echo=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)


async def upgrade_database(attempts=6, delay=10) -> None:
    for i in range(attempts):
        cmd = [sys.executable, '-m', 'alembic', 'upgrade', 'head']
        r = subprocess.run(cmd, capture_output=False)
        if r.returncode == 0:
            return

        logger.warning('Database is not ready!')
        await asyncio.sleep(delay)
    raise RuntimeError('Can`t upgrade database!')


async def get_langs(session: AsyncSession) -> list[Lang]:
    query = select(Lang)
    result: Result = await session.execute(query)
    rows = result.fetchall()
    return [row[0] for row in rows]


async def get_user_lang(user_id: int,
                        session: AsyncSession) -> Lang | None:
    query = (
        select(Lang)
            .join(User, User.lang_id == Lang.id)
            .filter(User.id == user_id)
    )
    return await session.scalar(query)


async def get_lang_by_id(lang_id: int,
                         session: AsyncSession) -> Lang | None:
    query = select(Lang).where(Lang.id == lang_id)
    return await session.scalar(query)


async def get_lang_by_short(short: str,
                            session: AsyncSession) -> Lang | None:
    query = select(Lang).where(Lang.short == short)
    return await session.scalar(query)


async def get_lang_by_name(name: str,
                           session: AsyncSession) -> Lang | None:
    query = select(Lang).where(Lang.name == name)
    return await session.scalar(query)


async def update_user_lang(user_id: int,
                           lang_id: int,
                           session: AsyncSession):
    user = User(id=user_id, lang_id=lang_id)
    await session.merge(user)
