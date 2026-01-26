from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

from mangabot.database.crud import get_or_create_user, get_random_manga
from mangabot.messages.templates import message_start, message_manga, message_last_hapter_subsribe
from mangabot.bot.keyboards.inline import start_keyboard
from mangabot.bot.keyboards.reply import random_manga_keyboard

router = Router()

@router.message(CommandStart())
async def command_start_handler(message: Message):
    telegram_id = message.from_user.id
    username = message.from_user.full_name

    user = await get_or_create_user(telegram_id=telegram_id, username=username)

    if user:
        await message.answer(
            text=message_start(username),
            reply_markup=start_keyboard())
        await message.answer("Нажми кнопку ниже чтобы получить случайную мангу", reply_markup=random_manga_keyboard())
    else:
        await message.answer("Что-то пошло не так, попробуй позже.")

@router.callback_query(F.data.startswith("random_manga"))
async def handle_random_manga1(call: CallbackQuery):
    manga = await get_random_manga()
    message_content = message_manga(
        manga.title, manga.source, manga.photo_url, manga.url)
    await call.bot.send_message(call.from_user.id, message_content)
    await call.answer()


@router.message(F.text == 'Случайная манга')
async def handle_random_manga2(message: Message):
    manga = await get_random_manga()
    message_content = message_manga(
        manga.title, manga.source, manga.photo_url, manga.url)
    await message.answer(message_content)


@router.message(F.text == "Тест")
async def test(message: Message):
    await message.bot.send_message(
        message.from_user.id, 
        message_last_hapter_subsribe("Тестовое название", "Том 1 Глава 1", "https://remanga.org/manga/biting-habit-on-a-flower/1902659"))