import asyncio
import logging
from pathlib import Path
from contextlib import suppress

from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.i18n import I18n
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from database.utils import upgrade_database
from handlers import router
from middlewares import DEFAULT_LANG, LangMiddleware
from settings import Settings


async def run(settings: Settings):
    fmt = "[%(asctime)s] %(message)s (%(levelname)s) [%(name)s]"
    date_fmt = "%d.%m.%y %H:%M:%S"
    logging.basicConfig(level=logging.DEBUG, format=fmt, datefmt=date_fmt)
    for logger_name in ('asyncio', 'aiosqlite'):
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

    i18n = I18n(path="locales",
                default_locale=DEFAULT_LANG,
                domain="messages")
    lang_middleware = LangMiddleware(session_maker, i18n)
    await lang_middleware.init_langs()

    router.message.outer_middleware(lang_middleware)
    router.callback_query.outer_middleware(lang_middleware)

    await bot.delete_webhook()
    dp.include_router(router)
    await dp.start_polling(bot,
                           session_maker=session_maker,
                           lang_middleware=lang_middleware)


async def main():
    load_dotenv()
    settings = Settings()
    await run(settings)


if __name__ == '__main__':
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
