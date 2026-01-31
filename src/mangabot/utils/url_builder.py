from mangabot.bot.config import BASE_URL

def build_manga_url(source: str, url:str):
    base = BASE_URL.get(source)
    
    if not base:
        raise ValueError(f"Неизвестный источник {source}")
    
    return base + url
    
