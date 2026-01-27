from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from mangabot.bot.config import BOT_NAME, BOT_TOKEN
from mangabot.database.session import init_db
from mangabot.scheduler.tasks import check_new_chapters
from mangabot.bot.handlers.start import router as start_router
from mangabot.bot.handlers.inline import router as inline_router
from mangabot.bot.handlers.subscriptions import router as subs_router
from mangabot.bot.handlers.settings import router as settings_router
from mangabot.utils.logger import logger

async def start_bot():
    try:
        logger.info("Запуск бота")
        bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

        dp = Dispatcher()

        dp.include_router(start_router)
        dp.include_router(inline_router)
        dp.include_router(subs_router)
        dp.include_router(settings_router)
        
        await init_db()
        logger.info("База данных инициализирована")

        scheduler = AsyncIOScheduler()
        scheduler.add_job(check_new_chapters, 'interval',
                          minutes=2, args=[bot])
        scheduler.start()
        logger.info("Планировщик запущен")
        
        logger.info("Бот готов к работе") 
        await dp.start_polling(bot)

    except Exception as e:
        logger.critical(f"Критическая ошибка при запуске бота: {e}", exc_info=True)
        raise