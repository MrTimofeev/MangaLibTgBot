from mangabot.database.model import User, Manga, Chapter, Subscription

from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy import func, delete

from mangabot.database.session import AsyncSessionLocal
from mangabot.messages.templates import message_last_hapter_subsribe
from mangabot.database.dto import MangaSave
import random


async def get_or_create_user(telegram_id: int, username: str):
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
            return new_user
        return user


async def set_age_verified(telegram_id: int, verifed: bool):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).filter_by(telegram_id=telegram_id))
        user = result.scalars().first()
        if user:
            user.age_verifed = verifed
            await session.commit()
            
async def set_preferred_sources(telegram_id: int, sources: list[str] | None):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).filter_by(telegram_id=telegram_id))
        user = result.scalars().first()
        if user:
            user.sources_list = sources
            await session.commit()
            

async def get_manga(
    search_text: str = "",
    preferred_source: list[str] | None = None,
    exclude_adult: bool = False
):
    async with AsyncSessionLocal() as session:
        query = select(Manga).where(Manga.search_title.ilike(f"%{search_text}%"))
        
        if preferred_source is not None:
            query = query.where(Manga.source.in_(preferred_source))
        
        if exclude_adult:
            query = query.where(Manga.is_adult == False)
            
        result = await session.execute(query.limit(40))
        return result.scalars().all()


async def save_manga(dto: MangaSave):
    async with AsyncSessionLocal() as session:
        # Проверяем, существует ли манга в базе
        result = await session.execute(select(Manga).filter_by(title=dto.title, source=dto.source))
        manga = result.scalars().first()

        if not manga:
            # Если манги нет, создаем новую запись
            new_manga = Manga(
                title=dto.title,
                search_title=dto.search_title,
                url=dto.url,
                last_chapter_number=dto.last_chapter_number,
                last_chapter_url=dto.last_chapter_url,
                photo_url=dto.photo_url,
                thumbnail_url=dto.thumbnail_url,
                source=dto.source
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


async def save_manga_and_chapter(dto: MangaSave, bot):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Manga).filter_by(title=dto.title, source=dto.source))
        manga = result.scalars().first()

        if not manga:
            # Если манги нет, создаем новую запись
            new_manga = Manga(
                title=dto.title,
                search_title=dto.search_title,
                url=dto.url,
                last_chapter_number=dto.last_chapter_number,
                last_chapter_url=dto.last_chapter_url,
                photo_url=dto.photo_url,
                thumbnail_url=dto.thumbnail_url,
                is_adult=dto.is_adult,
                status=dto.status,
                translate_status=dto.translate_status,
                source=dto.source
            )
            session.add(new_manga)
            await session.commit()
            await session.refresh(new_manga)

            # Создаем запись о новой главе
            new_chapter = Chapter(
                manga_id=new_manga.id,
                chapter_number=dto.last_chapter_number,
                chapter_url=dto.last_chapter_url
            )
            session.add(new_chapter)
            await session.commit()

        else:
            # Обновляем информацию о последней главе, если она изменилась
            if is_new_chapter(manga.last_chapter_number, dto.last_chapter_number):
                manga.last_chapter_number = dto.last_chapter_number
                manga.last_chapter_url = dto.last_chapter_url

                # Добавляем новую главу
                new_chapter = Chapter(
                    manga_id=manga.id,
                    chapter_number=dto.last_chapter_number,
                    chapter_url=dto.last_chapter_url
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
                            message_last_hapter_subsribe(dto.title, dto.last_chapter_number, dto.last_chapter_number)
                        )
                        # Обновляем последнюю уведомленную главу
                        subscription.last_notified_chapter = manga.last_chapter_number
                        await session.commit()



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

async def get_user_subscriptions(user_id: int):
    async with AsyncSessionLocal() as session:
        # Запрашиваем все подписки пользователя с подгрузкой связанной манги
        result = await session.execute(
            select(Subscription).filter_by(user_id=user_id).options(
                joinedload(Subscription.manga))
        )
        subscriptions = result.scalars().all()
        return subscriptions
