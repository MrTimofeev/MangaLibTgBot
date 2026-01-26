from mangabot.main import start_bot
import asyncio

if __name__ == "__main__":
    try:
        asyncio.run(start_bot())
    except (KeyboardInterrupt, SystemExit) as e:
        print(f"Ошибка при завершении: {e}")
