from aiogram.types import Update, Chat
from aiogram_i18n.managers import BaseManager
from aiogram_i18n import I18nMiddleware
from cachetools import LRUCache
from sqlalchemy.ext.asyncio import async_sessionmaker

import database


def get_locale_from_update(update: Update) -> str | None:
    if message := update.message:
        if from_user := message.from_user:
            if locale := from_user.language_code:
                return locale
    return None


class CustomManager(BaseManager):
    def __init__(self, default_locale: str | None = None) -> None:
        super().__init__(default_locale)

    async def set_locale(
        self,
        locale: str,
        event_chat: Chat,
        session_maker: async_sessionmaker,
        locales_cache: LRUCache,
    ) -> None:
        async with session_maker.begin() as session:
            await database.set_user_locale(event_chat.id, locale, session)
            locales_cache[event_chat.id] = locale

    async def get_locale(
        self,
        event,
        session_maker: async_sessionmaker,
        locales_cache: LRUCache,
        i18n_middleware: I18nMiddleware,
    ) -> str:
        if (
            not isinstance(event, Update)
            or event.message is None
            or event.message.chat is None
        ):
            return self.default_locale

        chat_id = event.message.chat.id
        if locale := locales_cache.get(chat_id):
            return locale

        async with session_maker.begin() as session:
            if locale := await database.get_user_locale(chat_id, session):
                locales_cache[chat_id] = locale
                return locale

            if locale := get_locale_from_update(event):
                if locale in i18n_middleware.core.locales:
                    locales_cache[chat_id] = locale
                    return locale

        return self.default_locale
