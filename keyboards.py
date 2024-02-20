from aiogram_i18n import LazyProxy
from aiogram_i18n.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from bot_types import LangData
from database.models import Lang


def main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton(text=LazyProxy("language")),
                KeyboardButton(text=LazyProxy("fruits")),
            ]
        ],
    )


def fruits_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton(text=LazyProxy("apple")),
                KeyboardButton(text=LazyProxy("banana")),
                KeyboardButton(text=LazyProxy("orange")),
            ],
            [
                KeyboardButton(text=LazyProxy("back")),
            ],
        ],
    )


def lang_keyboard(langs: list[Lang]) -> InlineKeyboardMarkup:
    buttons = []
    for lang in langs:
        button = InlineKeyboardButton(
            text=lang.name + " " + lang.flag, callback_data=LangData(id=lang.id).pack()
        )
        buttons.append(button)

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                button,
            ]
            for button in buttons
        ]
    )


def reload_keyboard() -> ReplyKeyboardMarkup:
    button = KeyboardButton(
        text="🔄 Reload",
    )
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[button]])
