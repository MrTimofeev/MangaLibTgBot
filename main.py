import asyncio
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from MangaBot.bot import handlers as handlers_manga_bot
from MangaBot.bot import config as config_manga_bot


async def start_bot(handlers, dp, config):
    try:
        bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(
            parse_mode=ParseMode.HTML))
        await handlers.on_startup(bot)
        print(f"Бот {config.BOT_NAME} инициализирован успешно")
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Ошибка при запуске бота {config.BOT_NAME}: {e}")


async def main() -> None:
    try:
        await start_bot(handlers_manga_bot,
                        handlers_manga_bot.dp_Manga_Bot, config_manga_bot)
    except Exception as e:
        print(f"Ошибка при запуске бота: {e}")


if __name__ == "__main__":
    # Запускаем основную функцию
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit) as e:
        print(f"Ошибка при завершении: {e}")
