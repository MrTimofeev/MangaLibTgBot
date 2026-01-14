import asyncio
from aiogram import Dispatcher, types, Router, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from mangabot.bot.config import *
import uuid
from mangabot.database.db import create_user, init_db, add_subscription_for_user, remove_subscription_for_user, get_user_subscriptions, get_manga, check_manga_by_id_in_db, get_random_manga, remove_all_subscriptions_for_user, count_user_subscriptions
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from mangabot.parser.mangalib.mangalib_parser_last_chapter import parse_manga

dp_Manga_Bot = Dispatcher(storage=MemoryStorage())
router = Router()


# Создаем клавиатуру с кнопкой, вставляющей имя бота в поле ввода
keyboard_start_inline = InlineKeyboardMarkup(

    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Манга на которую я подписан📚",
                callback_data="List_manga"
            )
        ],
        [
            InlineKeyboardButton(
                text="Найти мангу через бота 🔍",
                switch_inline_query_current_chat=" "  # Переход в inline-режим с пустым запросом
            )
        ],
        [
            InlineKeyboardButton(
                text="Удалить все подписки",
                callback_data="Delete_all_manga"
            )
        ]
    ]
)

keyboard_start_button = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(
                text="Случайная манга",
            )
        ]
    ]
)

# Кнопка для отписки от конкретной манги


def unsubscribe_keyboard(title):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отписаться!',
                                  callback_data=f"unsubscribe:{title}")]
        ]
    )


@dp_Manga_Bot.message(CommandStart())
async def command_start_handler(message: Message):
    telegram_id = message.from_user.id
    username = message.from_user.full_name

    user = await create_user(telegram_id=telegram_id, username=username, message=message)

    if user:
        await message.answer(
            text=f"""🎉 <b>Привет! {username}</b> Я — бот, который поможет тебе следить за выходом новых глав твоей любимой манги на <b>MangaLib</b>. 📚

🔍 <b>Как пользоваться:</b>
1. Введи название манги или воспользуйся поиском через <code>@Manga_Lib_Notify_Bot</code> в любом чате.
2. Найди нужный тайтл и нажми кнопку <b>«Подписаться!»</b>.

🚀 <b>Что дальше?</b>  
Как только выйдет новая глава, я отправлю тебе уведомление, чтобы ты первым узнал о продолжении! 💌

✨ Готов начать? Просто начни поиск и подписывайся на любимые тайтлы!""",
            reply_markup=keyboard_start_inline)
        await message.answer("Нажми кнопку ниже чтобы получить случайную мангу", reply_markup=keyboard_start_button)
    else:
        await message.answer("Что-то пошло не так, попробуй позже.")


def keyboard_template(title): return InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Подписаться!',
                              callback_data=f"subscribe:{title}")]
    ]
)


@dp_Manga_Bot.inline_query()
async def inline_search(query: types.InlineQuery):
    search_text = query.query.lower().strip()  # Убираем лишние пробелы
    print(f"Поисковый запрос: '{search_text}'")  # Логируем текст запроса

    # Если запрос пустой, возвращаем пустой ответ
    if not search_text:
        return await query.answer([], cache_time=60)

    results = []

    # Запрашиваем мангу с таймаутом на случай зависания
    try:
        anime_list = await asyncio.wait_for(get_manga(search_text), timeout=5)
    except asyncio.TimeoutError:
        print("Не удалось получить список манги из-за таймаута.")
        return await query.answer([], cache_time=60)

    if not anime_list:
        print(f"Нет результатов для запроса: {search_text}")
        return await query.answer([], cache_time=60)

    # Ограничиваем до 40 записей сразу в базе данных
    for anime in anime_list[:40]:  # Ограничение уже должно быть в get_manga
        result_id = str(uuid.uuid4())
        message_content = (
            f"<b>{anime.title}</b>\n"
            f'<a href="{anime.photo_url}">&#8205;</a>\n'
            f'Ссылка на мангу: <a href="{anime.url}">читать</a>'
        )

        results.append(
            types.InlineQueryResultArticle(
                id=result_id,
                title=anime.title,
                input_message_content=types.InputTextMessageContent(
                    message_text=message_content,
                    parse_mode="HTML"
                ),
                thumbnail_url=anime.thumbnail_url,
                thumbnail_width=400,
                thumbnail_height=400,
                reply_markup=keyboard_template(anime.id)
            )
        )

    print(f"Найдено {len(results)} результатов для запроса: {search_text}")

    # Отправляем ответ как можно быстрее
    try:
        await query.answer(results, cache_time=60, is_personal=True)
    except Exception as e:
        print(f"Ошибка при отправке inline-ответа: {e}")


@dp_Manga_Bot.callback_query(F.data.startswith("subscribe:"))
async def handle_subscribe(call: types.CallbackQuery):
    manga_id = call.data.split(':')[1]
    try:
        # Проверяем, есть ли манга в базе данных через импортированную функцию
        manga = await check_manga_by_id_in_db(manga_id)

        if manga:
            current_subscriptions_count = await count_user_subscriptions(call.from_user.id)
            if str(call.from_user.id) not in ADMIN and current_subscriptions_count >= int(MAX_SUBSCRIPTIONS):
                await call.bot.send_message(call.from_user.id, f"Вы достигли максимального количества подписок ({MAX_SUBSCRIPTIONS}). Удалите одну из подписок, чтобы добавить новую.")
                await call.answer()
                return

            # Манга найдена, добавляем подписку для пользователя
            subscription_added = await add_subscription_for_user(user_id=call.from_user.id, manga=manga)

            if subscription_added:
                await call.bot.send_message(call.from_user.id, f"Вы успешно подписались на обновления манги: {manga.title}")
            else:
                await call.bot.send_message(call.from_user.id, f"Вы уже подписаны на мангу: {manga.title}")
        else:
            # Манги нет в базе данных
            await call.bot.send_message(call.from_user.id, "Что-то пошло не так. Возможно, манга закончена или её нет в базе. Приносим свои извинения.")
    except Exception as e:
        print(f"Что-то пошло не так: {e}")
    await call.answer()


@dp_Manga_Bot.callback_query(F.data.startswith("List_manga"))
async def handle_manga_list(call: types.CallbackQuery):
    try:
        # Получаем список манги, на которую подписан пользователь
        subscriptions = await get_user_subscriptions(user_id=call.from_user.id)

        if subscriptions:

            for manga in subscriptions:
                await call.bot.send_message(
                    call.from_user.id,
                    f"📚 <b>{manga.manga.title}</b>\nСсылка на мангу: <a href='{manga.manga.url}'>читать</a>",
                    parse_mode="HTML",
                    reply_markup=unsubscribe_keyboard(manga.manga.id)
                )
        else:
            # Если у пользователя нет подписок
            await call.bot.send_message(call.from_user.id, "Вы не подписаны ни на одну мангу.")
    except Exception as e:
        # Обрабатываем возможные ошибки
        print(f"Произошла ошибка при получении списка подписок: {e}")
    finally:
        await call.answer()


# Обработчик нажатия на кнопку отписки
@dp_Manga_Bot.callback_query(F.data.startswith("unsubscribe:"))
async def handle_unsubscribe(call: types.CallbackQuery):
    manga_id = call.data.split(":")[1]
    try:
        # Проверяем, есть ли манга в базе данных
        manga = await check_manga_by_id_in_db(manga_id)

        if manga:
            # Манга найдена, пробуем удалить подписку
            subscription_removed = await remove_subscription_for_user(user_id=call.from_user.id, manga=manga)

            if subscription_removed:
                await call.bot.send_message(call.from_user.id, f"Вы успешно отписались от обновлений манги: {manga.title}")
            else:
                await call.bot.send_message(call.from_user.id, "Вы не были подписаны на эту мангу.")
        else:
            # Манги нет в базе данных
            await call.bot.send_message(call.from_user.id, "Манга не найдена в базе. Возможно, она уже удалена или вы не были на неё подписаны.")
    except Exception as e:
        # Обрабатываем возможные ошибки
        print(f"Произошла ошибка при удалении подписки: {e}")
    finally:
        await call.answer()


@dp_Manga_Bot.callback_query(F.data.startswith("Delete_all_manga"))
async def handle_manga_delete(call: types.CallbackQuery):
    success = await remove_all_subscriptions_for_user(call.from_user.id)

    if success:
        await call.bot.send_message(call.from_user.id, "Все подписки успешно удалены ✅")
    else:
        await call.bot.send_message(call.from_user.id, "Произошла ошибка при удалении подписок ❌")
    await call.answer()


@dp_Manga_Bot.callback_query(F.data.startswith("random_manga"))
async def handle_random_manga1(call: types.CallbackQuery):
    manga = await get_random_manga()
    message_content = f"""
<b>{manga.title}</b>
<a href="{manga.photo_url}">&#8205;</a>
Ссылка на мангу: <a href="{manga.url}">читать</a>
"""
    await call.bot.send_message(call.from_user.id, message_content)
    await call.answer()


@dp_Manga_Bot.message(F.text == 'Случайная манга')
async def handle_random_manga2(message: Message):
    manga = await get_random_manga()
    message_content = f"""
<b>{manga.title}</b>
<a href="{manga.photo_url}">&#8205;</a>
Ссылка на мангу: <a href="{manga.url}">читать</a>
"""
    await message.answer(message_content)

# Функция для инициализации базы данных при запуске


async def on_startup(manga_bot):
    await init_db()
    # Создаем и запускаем планировщик каждые 2 минуты
    scheduler = AsyncIOScheduler()
    scheduler.add_job(parse_manga, 'interval', minutes=2, args=[manga_bot])
    scheduler.start()
