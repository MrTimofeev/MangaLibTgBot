import os
from dotenv import load_dotenv


load_dotenv()
debug = True
if debug:
    BOT_TOKEN = os.getenv("BOT_TOKEN1_TG_debug")
else:
    BOT_TOKEN = os.getenv("BOT_TOKEN1_TG_relese")

ADMIN = os.getenv("ADMINS")
MAX_SUBSCRIPTIONS = os.getenv("MAX_SUBSCRIPTIONS")
BOT_NAME = "MANGA_BOT"

