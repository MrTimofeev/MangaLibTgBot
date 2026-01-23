from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from mangabot.database.model import Base


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

# Асинхронная функция для создания таблиц


async def init_db():
    async with engine.begin() as conn:
        print("Создаем таблицы...")
        await conn.run_sync(Base.metadata.create_all)
        print("Таблицы созданы.")
