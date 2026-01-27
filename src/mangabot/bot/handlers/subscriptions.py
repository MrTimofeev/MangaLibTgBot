from aiogram import F, Router

from aiogram.types import CallbackQuery

from mangabot.bot.keyboards.inline import unsubscribe_keyboard
from mangabot.database.crud import get_user_subscriptions, count_user_subscriptions, check_manga_by_id_in_db, add_subscription_for_user, remove_subscription_for_user, remove_all_subscriptions_for_user
from mangabot.messages.templates import message_manga_list
from mangabot.bot.config import ADMIN, MAX_SUBSCRIPTIONS
from mangabot.utils.logger import logger

router = Router()

@router.callback_query(F.data.startswith("subscribe:"))
async def handle_subscribe(call: CallbackQuery):
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
        logger.warning(f"Про подписке проишла ошибка: {e}")
    await call.answer()


@router.callback_query(F.data.startswith("List_manga"))
async def handle_manga_list(call: CallbackQuery):
    try:
        # Получаем список манги, на которую подписан пользователь
        subscriptions = await get_user_subscriptions(user_id=call.from_user.id)

        if subscriptions:

            for manga in subscriptions:
                await call.bot.send_message(
                    chat_id=call.from_user.id,
                    text=message_manga_list(manga.manga.title, manga.manga.url),
                    parse_mode="HTML",
                    reply_markup=unsubscribe_keyboard(manga.manga.id)
                )
        else:
            # Если у пользователя нет подписок
            await call.bot.send_message(call.from_user.id, "Вы не подписаны ни на одну мангу.")
    except Exception as e:
        logger.warning(f"Произошла ошибка при получаении списка подписок: {e}")
    finally:
        await call.answer()


# Обработчик нажатия на кнопку отписки
@router.callback_query(F.data.startswith("unsubscribe:"))
async def handle_unsubscribe(call: CallbackQuery):
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
        logger.warning(f"Произошла ошибка при удалении подписки: {e}")
    finally:
        await call.answer()


@router.callback_query(F.data.startswith("Delete_all_manga"))
async def handle_manga_delete(call: CallbackQuery):
    success = await remove_all_subscriptions_for_user(call.from_user.id)

    if success:
        await call.bot.send_message(call.from_user.id, "Все подписки успешно удалены ✅")
    else:
        await call.bot.send_message(call.from_user.id, "Произошла ошибка при удалении подписок ❌")
    await call.answer()
