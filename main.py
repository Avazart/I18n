import asyncio
import logging
import os
from contextlib import suppress
from typing import Optional, Dict, Any

from aiogram import Dispatcher, Bot, Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton,
    TelegramObject, CallbackQuery
)
from aiogram.utils.i18n import I18n, I18nMiddleware
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __

from dotenv import load_dotenv

router = Router()


class LangMiddleware(I18nMiddleware):
    def __init__(self,
                 i18n: I18n,
                 i18n_key: Optional[str] = "i18n",
                 middleware_key: str = "i18n_middleware"):
        super().__init__(i18n, i18n_key, middleware_key)

    @staticmethod
    def _get_message(event: TelegramObject) -> Message:
        if isinstance(event, Message):
            return event
        elif isinstance(event, CallbackQuery):
            return event.message
        raise RuntimeError('Wrong event!')

    async def get_locale(self, event: TelegramObject,
                         data: Dict[str, Any]) -> str:
        logging.debug(self._get_message(event))
        return 'uk'


def fruits_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[[
            KeyboardButton(text=_('Apple')),
            KeyboardButton(text=_('Banana')),
            KeyboardButton(text=_('Orange'))
        ],
        ]
    )


@router.message(Command(commands=['start', ]))
async def start_command(message: Message):
    await message.answer(_("Hello!"), reply_markup=fruits_keyboard())


@router.message(F.text == __('Apple'))
async def apple(message: Message):
    await message.answer("🍎")


@router.message(F.text == __('Banana'))
async def banana(message: Message):
    await message.answer("🍌")


@router.message(F.text == __('Orange'))
async def orange(message: Message):
    await message.answer("🍊")


async def main():
    load_dotenv()

    fmt = "[%(asctime)s] %(message)s (%(levelname)s) [%(name)s]"
    date_fmt = "%d.%m.%y %H:%M:%S"
    logging.basicConfig(level=logging.DEBUG, format=fmt, datefmt=date_fmt)
    for logger_name in ('asyncio',):
        logging.getLogger(logger_name).setLevel(level=logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.debug("Run bot ...")

    logger.info("Create bot instance ...")

    bot = Bot(token=os.environ["TOKEN"], parse_mode="HTML")
    dp = Dispatcher()

    i18n = I18n(path="locales",
                default_locale='en',
                domain="messages")
    lang_middleware = LangMiddleware(i18n)

    router.message.outer_middleware(lang_middleware)
    router.callback_query.outer_middleware(lang_middleware)
    
    await bot.delete_webhook()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
