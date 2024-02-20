import logging

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram_i18n import I18nContext, LazyProxy
from sqlalchemy.ext.asyncio import async_sessionmaker

import database
from bot_types import LocaleData
from keyboards import (
    main_keyboard,
    fruits_keyboard,
    lang_keyboard,
    reload_keyboard,
)

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command(commands=["start"]))
async def start_command(
    message: Message,
    i18n: I18nContext,
    session_maker: async_sessionmaker,
):
    logger.debug("Start")

    async with session_maker.begin() as session:
        user_id = message.chat.id
        locale = await database.get_user_locale(user_id, session)
        logger.debug(f"{user_id=}, {locale=}")

    user_mention = message.from_user.mention_html()
    await message.answer(
        i18n.get("hello", user=user_mention),
        reply_markup=main_keyboard(),
    )


@router.message(F.text.endswith("Reload"))
@router.message(F.text == LazyProxy("back"))
async def back(message: Message, i18n: I18nContext):
    await message.answer(
        i18n.get("select_option"),
        reply_markup=main_keyboard(),
    )


@router.message(F.text == LazyProxy("fruits"))
async def fruits(message: Message, i18n: I18nContext):
    logger.debug("Fruits")
    await message.answer(
        i18n.get("fruits"),
        reply_markup=fruits_keyboard(),
    )


@router.message(F.text == LazyProxy("apple"))
async def get_apple(message: Message):
    await message.answer("🍎", reply_markup=fruits_keyboard())


@router.message(F.text == LazyProxy("banana"))
async def get_banana(message: Message):
    await message.answer("🍌", reply_markup=fruits_keyboard())


@router.message(F.text == LazyProxy("orange"))
async def get_orange(message: Message):
    await message.answer("🍊", reply_markup=fruits_keyboard())


# @router.message(
#     F.text.in_(
#         (
#                 LazyProxy("apple"),
#                 LazyProxy("banana"),
#                 LazyProxy("orange"),
#         )
#     )
# )
# async def get_fruit(message: Message, i18n: I18nContext):
#     fruits_ = {
#         LazyProxy("apple"): "🍎",
#         LazyProxy("banana"): "🍌",
#         LazyProxy("orange"): "🍊",
#     }
#     logger.debug(message.text)
# await message.answer(
#     fruits_[message.text],
#     reply_markup=fruits_keyboard(),
# )


@router.message(Command(commands=["lang"]))
@router.message(F.text == LazyProxy("language"))
async def language(message: Message, i18n: I18nContext):
    locales = {}
    for locale in i18n.core.locales:
        name = i18n.core.get("locale_name", locale)
        flag = i18n.core.get("locale_flag", locale)
        locales[locale] = dict(name=name, flag=flag)

    markup = lang_keyboard(locales)
    await message.answer(
        i18n.get("languages"),
        reply_markup=markup,
    )


@router.callback_query(LocaleData.filter())
async def set_language(
    query: CallbackQuery,
    callback_data: LocaleData,
    i18n: I18nContext,
):
    logger.debug("set_language")

    await i18n.set_locale(callback_data.locale)

    name = i18n.get("locale_name")
    flag = i18n.get("locale_flag")
    await query.message.answer(
        i18n.get("new_language", lang=name, flag=flag),
        reply_markup=reload_keyboard(),
    )
