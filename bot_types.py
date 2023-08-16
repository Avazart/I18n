from aiogram.filters.callback_data import CallbackData


class LangData(CallbackData, **dict(prefix='lang')):
    id: int
