import logging

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram_i18n import I18nContext, LazyProxy

import database
from bot_types import LangData
from keyboards import main_keyboard, fruits_keyboard, lang_keyboard, \
    reload_keyboard

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command(commands=["start"]))
async def start_command(
        message: Message,
        i18n: I18nContext,
        session_maker,
):
    logger.debug("Start")

    async with session_maker.begin() as session:
        user_id = message.chat.id
        lang = await database.get_user_lang(user_id, session)
        logger.debug(f"{user_id=}, {lang=}")

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


@router.message(
    F.text.in_(
        (
                LazyProxy("apple"),
                LazyProxy("banana"),
                LazyProxy("orange"),
        )
    )
)
async def get_fruit(message: Message, i18n: I18nContext):
    fruits_ = {
        LazyProxy("apple"): "🍎",
        LazyProxy("banana"): "🍌",
        LazyProxy("orange"): "🍊",
    }
    logger.debug(message.text)
    # await message.answer(
    #     fruits_[message.text],
    #     reply_markup=fruits_keyboard(),
    # )


@router.message(Command(commands=["lang"]))
@router.message(F.text == LazyProxy("language"))
async def language(
        message: Message,
        i18n: I18nContext,
        session_maker,
):
    async with session_maker.begin() as session:
        langs = await database.get_langs(session)
        markup = lang_keyboard(langs)
        await message.answer(
            i18n.get("languages"),
            reply_markup=markup,
        )


@router.callback_query(LangData.filter())
async def set_language(
        query: CallbackQuery,
        callback_data: LangData,
        i18n: I18nContext,
        session_maker,
):
    logger.debug("set_language")
    async with session_maker.begin() as session:
        chat_id = query.message.chat.id
        lang_id = callback_data.id
        logger.debug(f"Set {lang_id=}")

        lang = await database.get_lang_by_id(lang_id, session)
        await i18n.set_locale(lang.short, chat_id=chat_id)

        await query.message.answer(
            i18n.get("new_language", lang=lang.name, flag=lang.flag),
            reply_markup=reload_keyboard(),
        )
