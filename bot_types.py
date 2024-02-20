from aiogram.filters.callback_data import CallbackData


class LocaleData(CallbackData, prefix="locale"):
    locale: str
