import logging
import sys
from pathlib import Path


LOG_DIR = Path('logs')
LOG_DIR.mkdir(exist_ok=True)


LOG_FILE = LOG_DIR / "mangabot.log"


foomatter = logging.Formatter(
    fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger("MangaBot")
logger.setLevel(logging.DEBUG) 

# Хендлеры для файла (все, влючая DEBUG)
file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(foomatter)

# Хендлер для консоли (Только INFO и выше)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(foomatter)

# Добаляем хендлеры
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Запрещаем дублирование, если модуль импортируется несколько раз
logger.propagate = False

