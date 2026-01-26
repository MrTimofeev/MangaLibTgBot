from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Манга на которую я подписан📚", callback_data="List_manga")],
        # Переход в inline-режим с пустым запросом
        [InlineKeyboardButton(text="Найти мангу через бота 🔍",
                              switch_inline_query_current_chat=" ")],
        [InlineKeyboardButton(text="Удалить все подписки",
                              callback_data="Delete_all_manga")]
    ])


def subscribe_keyboard(manga_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подписаться!",
                              callback_data=f"subscribe: {manga_id}")]
    ])


def unsubscribe_keyboard(manga_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отписаться!',
                                  callback_data=f"unsubscribe:{manga_id}")]
        ])
