def message_help() -> str:
    return """
Привет для работы с ботом используй следующие команды:
1) /subscribe "название манги" для подписки на уведомления
2) /unsubscribe "название манги" для отписки на уведомления
3) /list для просмотра подписок на уведомления
"""


def message_manga(title: str, source: str, photo_url: str, url: str) -> str:
    return f"""<b>{title}</b>\n{source}\n<a href="{photo_url}">&#8205;</a>\n Ссылка на мангу: <a href="{url}">читать</a>"""

def message_manga_list(title: str, url: str) -> str:
    return f"📚 <b>{title}</b>\nСсылка на мангу: <a href='{url}'>читать</a>"

def message_start(username: str) -> str:
    return f"""🎉 <b>Привет! {username}</b> Я — бот, который поможет тебе следить за выходом новых глав твоей любимой манги на <b>MangaLib</b>. 📚

🔍 <b>Как пользоваться:</b>
1. Введи название манги или воспользуйся поиском через <code>@Manga_Lib_Notify_Bot</code> в любом чате.
2. Найди нужный тайтл и нажми кнопку <b>«Подписаться!»</b>.

🚀 <b>Что дальше?</b>  
Как только выйдет новая глава, я отправлю тебе уведомление, чтобы ты первым узнал о продолжении! 💌

✨ Готов начать? Просто начни поиск и подписывайся на любимые тайтлы!"""



def message_last_hapter_subsribe(title: str, chapter_number:str, chapter_url: str) -> str:
    return f"""<b>Новая глава манги {title}!\n{chapter_number}</b>\nСсылка на последнюю главу: <a href="{chapter_url}">читать</a>"""
