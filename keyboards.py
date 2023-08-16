from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup,
)
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __

from bot_types import LangData
from database.models import Lang


def main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[[
            KeyboardButton(text=_('Language')),
            KeyboardButton(text=_('Fruits')),
        ]]
    )


def fruits_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[[
            KeyboardButton(text=_('Apple')),
            KeyboardButton(text=_('Banana')),
            KeyboardButton(text=_('Orange'))
        ],
            [KeyboardButton(text=_('Back')), ]
        ]
    )


def lang_keyboard(langs: list[Lang]) -> InlineKeyboardMarkup:
    buttons = []
    for lang in langs:
        button = InlineKeyboardButton(
            text=lang.name + " " + lang.flag,
            callback_data=LangData(id=lang.id).pack()
        )
        buttons.append(button)

    return InlineKeyboardMarkup(
        inline_keyboard=[[button, ] for button in buttons]
    )


def reload_keyboard() -> ReplyKeyboardMarkup:
    button = KeyboardButton(
        text="🔄 Reload",
    )
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[[button],]
    )