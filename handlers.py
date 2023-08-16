import logging

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __

import database
from bot_types import LangData
from keyboards import main_keyboard, fruits_keyboard, lang_keyboard, \
    reload_keyboard
from middlewares import LangMiddleware

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command(commands=['start', ]))
async def start_command(message: Message, session_maker):
    logger.debug("Start")
    async with session_maker.begin() as session:
        user_id = message.chat.id
        lang = await database.get_user_lang(user_id, session)
        logger.debug(f"{user_id=}, {lang=}")
    await message.answer(_("Hello!"), reply_markup=main_keyboard())


@router.message(F.text.endswith('Reload'))
@router.message(F.text == __("Back"))
async def back(message: Message):
    await message.answer(
        _("Select option"),
        reply_markup=main_keyboard()
    )


@router.message(F.text == __("Fruits"))
async def fruits(message: Message):
    logger.debug("Fruits")
    await message.answer(_("Fruits"), reply_markup=fruits_keyboard())


@router.message(F.text.in_((__('Apple'), __('Banana'), __('Orange'))))
async def get_fruit(message: Message):
    fruits_ = {
        _('Apple'): "🍎",
        _('Banana'): "🍌",
        _('Orange'): "🍊"
    }
    logger.debug(message.text)
    await message.answer(fruits_[message.text],
                         reply_markup=fruits_keyboard())


@router.message(Command(commands=['lang', ]))
@router.message(F.text == __('Language'))
async def language(message: Message, session_maker):
    async with session_maker.begin() as session:
        langs = await database.get_langs(session)
        markup = lang_keyboard(langs)
        await message.answer("Languages", reply_markup=markup)


@router.callback_query(LangData.filter())
async def set_language(query: CallbackQuery,
                       callback_data: LangData,
                       session_maker,
                       lang_middleware: LangMiddleware):
    logger.debug("set_language")
    async with session_maker.begin() as session:
        chat_id = query.message.chat.id
        lang_id = callback_data.id
        logger.debug(f"Set {lang_id=}")
        lang = await database.get_lang_by_id(lang_id, session)
        await lang_middleware.update_user_lang(chat_id, lang_id)

        await query.message.answer(
            _("New language: {}").format(f"{lang.name} {lang.flag}"),
            reply_markup=reload_keyboard()
        )
