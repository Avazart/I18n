import logging
from typing import Dict, Any, Optional

from aiogram.types import Message, TelegramObject, CallbackQuery, User, Chat, \
    ErrorEvent
from aiogram.utils.i18n import I18nMiddleware, I18n
from cachetools import LRUCache

import database

logger = logging.getLogger(__name__)

DEFAULT_LANG = 'en'


class LangMiddleware(I18nMiddleware):
    def __init__(self, session_maker,
                 i18n: I18n,
                 i18n_key: Optional[str] = "i18n",
                 middleware_key: str = "i18n_middleware"):
        super().__init__(i18n, i18n_key, middleware_key)
        self._session_maker = session_maker
        self._cache = LRUCache(maxsize=1000)
        self._langs = frozenset()

    async def init_langs(self):
        async with self._session_maker.begin() as session:
            self._langs = frozenset(
                lang.short for lang in await database.get_langs(session)
            )

    @staticmethod
    def _get_message(event: TelegramObject) -> Message | None:
        if isinstance(event, Message):
            return event
        elif isinstance(event, CallbackQuery):
            return event.message
        return None
        #else:
        #    raise RuntimeError(f'Wrong event! {type(event)}')

    async def get_locale(self, event: TelegramObject,
                         data: Dict[str, Any]) -> str:
        if (m := self._get_message(event)) is None:
            return DEFAULT_LANG

        # 1. check cache
        if lang_short := self._cache.get(m.chat.id):
            return lang_short

        # 2. check db
        async with self._session_maker.begin() as session:
            if lang := await database.get_user_lang(m.chat.id, session):
                self._cache[m.chat.id] = lang.short
                return lang.short

            # 3. check language_code
            if m.from_user.language_code in self._langs:
                if lang := await database.get_lang_by_short(
                        m.from_user.language_code,
                        session
                ):
                    await database.update_user_lang(m.chat.id,
                                                    lang.id,
                                                    session)
                    self._cache[m.chat.id] = m.from_user.language_code
                    return m.from_user.language_code
        return DEFAULT_LANG

    async def update_user_lang(self, chat_id: int, lang_id: int) -> None:
        async with self._session_maker.begin() as session:
            await database.update_user_lang(chat_id, lang_id, session)
            lang = await database.get_lang_by_id(lang_id, session)
            self._cache[chat_id] = lang.short
