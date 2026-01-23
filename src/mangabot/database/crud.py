from mangabot.database.model import User, Manga, Chapter, Subscription

from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy import func, delete

from mangabot.database.session import AsyncSessionLocal
from mangabot.bot.message import message_last_hapter_subsribe
import random


async def create_user(telegram_id: int, username: str, message):
    async with AsyncSessionLocal() as session:
        # Проверяем, существует ли пользователь
        result = await session.execute(select(User).filter_by(telegram_id=telegram_id))
        user = result.scalars().first()

        if not user:
            # Если пользователя нет, создаем нового
            new_user = User(telegram_id=telegram_id, username=username)
            session.add(new_user)
            await session.commit()  # Асинхронный коммит
            await session.refresh(new_user)  # Обновляем объект пользователя
            await message.bot.send_message(
                chat_id=1406453685,
                text=f"Новый пользователь добавлен: {username} (ID: {telegram_id})")
            return new_user
        return user


async def get_manga(search_text: str = ""):
    async with AsyncSessionLocal() as session:
        query = select(Manga).where(
            # Поиск без учета регистра
            Manga.search_title.ilike(f"%{search_text}%")
        ).limit(40)  # Ограничение на 40 записей
        result = await session.execute(query)
        return result.scalars().all()


async def get_manga_by_title(title: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Manga).filter_by(title=title))
        manga = result.scalars().first()
        return manga


async def update_manga_titles_to_lowercase():
    async with AsyncSessionLocal() as session:
        # Запрашиваем все манги
        result = await session.execute(select(Manga))
        mangas = result.scalars().all()

        # Обновляем каждое название в нижнем регистре
        for manga in mangas:
            manga.title = manga.title.lower()  # Приводим название к нижнему регистру

        # Сохраняем изменения
        await session.commit()

        print(f"Обновлено названий манги: {len(mangas)}")


async def get_user_by_telegram_id(telegram_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).filter_by(telegram_id=telegram_id))
        user = result.scalars().first()
        return user


async def get_subscriptions_for_user(user_id: int):
    async with AsyncSessionLocal() as session:
        # Выполняем запрос для получения подписок пользователя
        result = await session.execute(select(Subscription).filter_by(user_id=user_id))
        subscriptions = result.scalars().all()
        return subscriptions


async def save_manga(title: str, search_title: str, manga_url: str, chapter_number: str, chapter_url: str, photo_url: str, thumbnail_url: str, source: str):
    async with AsyncSessionLocal() as session:
        # Проверяем, существует ли манга в базе
        result = await session.execute(select(Manga).filter_by(title=title, source=source))
        manga = result.scalars().first()

        if not manga:
            # Если манги нет, создаем новую запись
            new_manga = Manga(
                title=title,
                search_title=search_title,
                url=manga_url,
                last_chapter_number=chapter_number,
                last_chapter_url=chapter_url,
                photo_url=photo_url,
                thumbnail_url=thumbnail_url,
                source=source
            )
            session.add(new_manga)
            await session.commit()
            await session.refresh(new_manga)


def parse_chapter_number(chapter_number: str) -> tuple[int, float]:
    """
    Извлекает номер тома и главы.
    Глава может быть в формате '32.1'.
    Возвращает кортеж (volume, chapter) с целым и дробным числами.
    """
    parts = chapter_number.split()
    volume = int(parts[1])  # 'Том X'
    chapter = float(parts[3])  # 'Глава Y' или 'Глава 32.1'
    return volume, chapter


def is_new_chapter(current: str, new: str) -> bool:
    """Сравнивает две главы по томам и номерам."""
    current_volume, current_chapter = parse_chapter_number(current)
    new_volume, new_chapter = parse_chapter_number(new)

    # Сначала проверяем том, затем номер главы
    if new_volume > current_volume:
        return True
    elif new_volume == current_volume and new_chapter > current_chapter:
        return True
    return False


async def save_manga_and_chapter(title: str, search_title: str, manga_url: str, chapter_number: str, chapter_url: str, photo_url: str, thumbnail_url: str, source: str, bot):
    async with AsyncSessionLocal() as session:
        # Проверяем, существует ли манга в базе
        result = await session.execute(select(Manga).filter_by(title=title))
        manga = result.scalars().first()

        if not manga:
            # Если манги нет, создаем новую запись
            new_manga = Manga(
                title=title,
                search_title=search_title,
                url=manga_url,
                last_chapter_number=chapter_number,
                last_chapter_url=chapter_url,
                photo_url=photo_url,
                thumbnail_url=thumbnail_url,
                source=source
            )
            session.add(new_manga)
            await session.commit()
            await session.refresh(new_manga)

            # Создаем запись о новой главе
            new_chapter = Chapter(
                manga_id=new_manga.id,
                chapter_number=chapter_number,
                chapter_url=chapter_url
            )
            session.add(new_chapter)
            await session.commit()

            return new_manga
        else:
            # Обновляем информацию о последней главе, если она изменилась
            if is_new_chapter(manga.last_chapter_number, chapter_number):
                manga.last_chapter_number = chapter_number
                manga.last_chapter_url = chapter_url

                # Добавляем новую главу
                new_chapter = Chapter(
                    manga_id=manga.id,
                    chapter_number=chapter_number,
                    chapter_url=chapter_url
                )
                session.add(new_chapter)
                await session.commit()

                subscriptions_result = await session.execute(
                    select(Subscription).filter_by(manga_id=manga.id)
                )

                subscriptions = subscriptions_result.scalars().all()
                # Уведомляем каждого подписчика
                for subscription in subscriptions:
                    # Если новая глава больше последней уведомленной главы, отправляем уведомление
                    if subscription.last_notified_chapter < manga.last_chapter_number:
                        # Отправка сообщения пользователю
                        await bot.send_message(
                            subscription.user_id,
                            message_last_hapter_subsribe(title, chapter_number, chapter_url)
                        )
                        # Обновляем последнюю уведомленную главу
                        subscription.last_notified_chapter = manga.last_chapter_number
                        await session.commit()

            return manga


# Функция для добавления подписки пользователя на мангу
async def add_subscription_for_user(user_id: int, manga: Manga) -> bool:
    async with AsyncSessionLocal() as session:
        # Проверяем, есть ли уже подписка на эту мангу
        result = await session.execute(select(Subscription).filter_by(user_id=user_id, manga_id=manga.id))
        subscription = result.scalars().first()

        if subscription:
            return False  # Пользователь уже подписан на эту мангу

        # Добавляем подписку
        new_subscription = Subscription(
            user_id=user_id, manga_id=manga.id, last_notified_chapter=manga.last_chapter_number)
        session.add(new_subscription)
        await session.commit()
        return True

# Функция для проверки, существует ли манга в базе данных


async def check_manga_by_id_in_db(id) -> Manga:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Manga).filter_by(id=id))
        manga = result.scalars().first()
        return manga


async def get_random_manga() -> Manga:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(func.count(Manga.id)))
        count_manga = result.scalar()  # Получаем количество манг

        if count_manga == 0:
            # Обработка пустой таблицы
            raise ValueError("В таблице нет записей")

        random_id_manga = random.randint(1, count_manga)
        return await check_manga_by_id_in_db(random_id_manga)


async def count_user_subscriptions(user_id: int) -> int:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(func.count(Subscription.user_id)).where(
                Subscription.user_id == user_id)
        )
        return result.scalar()  # Возвращает количество подписок

# Функция для проверки, существует ли манга в базе данных


async def check_manga_in_db(url: str) -> Manga:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Manga).filter_by(url=url))
        manga = result.scalars().first()
        return manga


async def remove_all_subscriptions_for_user(user_id: int) -> bool:
    async with AsyncSessionLocal() as session:
        try:
            # Удаляем все подписки для данного пользователя
            await session.execute(
                delete(Subscription).where(Subscription.user_id == user_id)
            )
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()  # Откат транзакции в случае ошибки
            print(f"Ошибка при удалении подписок: {e}")
            return False


# Функция для удаления подписки пользователя на мангу


async def remove_subscription_for_user(user_id: int, manga: Manga) -> bool:
    async with AsyncSessionLocal() as session:
        # Проверяем, есть ли подписка на эту мангу
        result = await session.execute(select(Subscription).filter_by(user_id=user_id, manga_id=manga.id))
        subscription = result.scalars().first()

        if subscription:
            # Если подписка найдена, удаляем её
            await session.delete(subscription)
            await session.commit()
            return True
        return False  # Подписка не найдена

# Функция для получения подписок пользователя


async def get_user_subscriptions(user_id: int):
    async with AsyncSessionLocal() as session:
        # Запрашиваем все подписки пользователя с подгрузкой связанной манги
        result = await session.execute(
            select(Subscription).filter_by(user_id=user_id).options(
                joinedload(Subscription.manga))
        )
        subscriptions = result.scalars().all()
        return subscriptions
