import asyncio
import logging
import os
from contextlib import suppress
from typing import Any

from aiogram import Dispatcher, Bot, Router, F
from aiogram.filters import Command
from aiogram.types import Message, Update

from aiogram_i18n import I18nMiddleware, I18nContext, LazyProxy
from aiogram_i18n.cores.fluent_runtime_core import FluentRuntimeCore
from aiogram_i18n.managers import BaseManager
from aiogram_i18n.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from dotenv import load_dotenv

router = Router()

def get_lang_code_from_update(update: Update) -> str | None:
    if message := update.message:
        if from_user := message.from_user:
            if lang_code := from_user.language_code:
                return lang_code
    return None

class CustomBaseManager(BaseManager):
    SUPPORTED_LANG_CODES = ["en", "uk"]

    def __init__(self, default_locale: str | None = "en") -> None:
        super().__init__(default_locale)

    async def set_locale(self, *args: Any, **kwargs: Any) -> None:
        pass

    async def get_locale(self, *args: Any, **kwargs: Any) -> str:
        """
        FIXME:
           Мабуть не дуже гарний спосіб бо не враховує
           всі можливі випадки але ...
        """
        if event := kwargs.get("event"):
            if isinstance(event, Update):
                lang_code = get_lang_code_from_update(event)
                if lang_code and lang_code in self.SUPPORTED_LANG_CODES:
                    return lang_code
        return self.default_locale


def fruits_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton(text=LazyProxy("apple")),
                KeyboardButton(text=LazyProxy("banana")),
                KeyboardButton(text=LazyProxy("orange")),
            ],
        ],
    )


@router.message(Command(commands=["start"]))
async def start_command(message: Message, i18n: I18nContext):
    name = message.from_user.mention_html()
    await message.answer(
        i18n.get("hello", user=name),
        reply_markup=fruits_keyboard(),
    )


@router.message(F.text == LazyProxy("apple"))
async def apple(message: Message, i18n: I18nContext):
    await message.answer("🍎")


@router.message(F.text == LazyProxy("banana"))
async def banana(message: Message, i18n: I18nContext):
    await message.answer("🍌")


@router.message(F.text == LazyProxy("orange"))
async def orange(message: Message, i18n: I18nContext):
    await message.answer("🍊")


async def main():
    load_dotenv()

    fmt = "[%(asctime)s] %(message)s (%(levelname)s) [%(name)s]"
    date_fmt = "%d.%m.%y %H:%M:%S"
    logging.basicConfig(level=logging.DEBUG, format=fmt, datefmt=date_fmt)
    for logger_name in ("asyncio",):
        logging.getLogger(logger_name).setLevel(level=logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.debug("Run bot ...")

    logger.info("Create bot instance ...")

    bot = Bot(token=os.environ["TOKEN"], parse_mode="HTML")
    dp = Dispatcher()

    i18n_middleware = I18nMiddleware(
        core=FluentRuntimeCore(path="locales/{locale}/LC_MESSAGES"),
        manager=CustomBaseManager(),
    )
    i18n_middleware.setup(dispatcher=dp)

    await bot.delete_webhook()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
