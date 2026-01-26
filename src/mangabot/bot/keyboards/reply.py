from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def random_manga_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Случайная манга")],
            [KeyboardButton(text="🔞 Подтвердить возраст")],
            [KeyboardButton(text="⚙️ Настройки источников")]
        ],
        resize_keyboard=True,
    )
