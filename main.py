import asyncio
import logging
from contextlib import suppress

from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram_i18n import I18nMiddleware
from aiogram_i18n.cores.fluent_runtime_core import FluentRuntimeCore
from cachetools import LRUCache
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

import database
from custom_manager import CustomManager
from database.utils import upgrade_database
from handlers import router
from settings import Settings


async def run(settings: Settings):
    fmt = "[%(asctime)s] %(message)s (%(levelname)s) [%(name)s]"
    date_fmt = "%d.%m.%y %H:%M:%S"
    logging.basicConfig(level=logging.DEBUG, format=fmt, datefmt=date_fmt)
    for logger_name in ("asyncio", "aiosqlite"):
        logging.getLogger(logger_name).setLevel(level=logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.debug("Run bot ...")

    logger.info("Upgrade database ...")
    await upgrade_database(attempts=1)

    logger.info("Create database engine ...")
    engine = create_async_engine(settings.database_url, echo=False)
    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    logger.info("Create bot instance ...")

    bot = Bot(token=settings.token, parse_mode="HTML")
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    lang_cache = LRUCache(maxsize=1000)
    async with session_maker.begin() as session:
        supported_lang_codes = frozenset(
            lang.short for lang in await database.get_langs(session)
        )

    i18n_middleware = I18nMiddleware(
        core=FluentRuntimeCore(path="locales/{locale}"),
        manager=CustomManager(),
    )
    i18n_middleware.setup(dispatcher=dp)

    await bot.delete_webhook()
    dp.include_router(router)
    await dp.start_polling(
        bot,
        session_maker=session_maker,
        lang_cache=lang_cache,
        supported_lang_codes= supported_lang_codes
    )


async def main():
    load_dotenv()
    settings = Settings()
    await run(settings)


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
