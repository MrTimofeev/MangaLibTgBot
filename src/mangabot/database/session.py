from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

from mangabot.utils.logger import logger


Base = declarative_base()
# Создание асинхронного движка для работы с SQLite
DATABASE_URL = "sqlite+aiosqlite:///./manga_bot.db"

# Создаем асинхронный движок
engine = create_async_engine(DATABASE_URL, echo=False)


# Настраиваем фабрику для создания асинхронных сессий
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,  # Используем асинхронную сессию
    expire_on_commit=False
)


async def init_db():
    async with engine.begin() as conn:
        logger.info("Создаем таблицы...")
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Таблицы созданы.")
