from mangabot.main import start_bot
from mangabot.utils.logger import logger
import asyncio

if __name__ == "__main__":
    try:
        asyncio.run(start_bot())
    except (KeyboardInterrupt, SystemExit) as e:
        logger.critical(f"Ошибка при завершении: {e}")
