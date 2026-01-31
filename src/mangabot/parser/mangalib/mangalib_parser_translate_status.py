import asyncio
import requests
import pprint
import httpx
import random

from sqlalchemy.future import select


from mangabot.database.model import Manga
from mangabot.database.session import init_db, AsyncSessionLocal
from mangabot.utils.logger import logger

HEADERS = {
    'sec-ch-ua-platform': '"Windows"',
    'Referer': 'https://mangalib.org/',
    'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
    'sec-ch-ua-mobile': '?0',
    'Site-Id': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
    'Client-Time-Zone': 'Europe/Moscow',
    'DNT': '1',
    'Content-Type': 'application/json',
}


async def sync_parse():
    await init_db()
    async with AsyncSessionLocal() as session:
        async with httpx.AsyncClient() as client:
            result = await session.scalars(select(Manga).filter(Manga.translate_status.is_(None), Manga.source == "mangalib")) 
                
            for item in result:
                logger.debug(f"Обрабатываю {item.title}")
                url_manga = f"{item.url.replace("https://mangalib.org/ru/manga/", "https://api.cdnlibs.org/api/manga/")}?&fields[]=manga_status_id&fields[]=status_id"
                try:
                    response = await client.get(url_manga, headers=HEADERS, timeout=15.0)
                    response.raise_for_status()
                    data = response.json()
                    item.translate_status = data["data"]['scanlateStatus'].get('label', None)
                    item.status = data["data"]['status'].get('label', None)
                    await session.commit()
                    
                except (httpx.HTTPError, ValueError) as e:
                    logger.error(f"Ошибка при загрузке {url_manga}: {e}")
                    item.translate_status = None
                    await session.commit()
                
                await asyncio.sleep(random.randint(2, 5))
        
    
asyncio.run(sync_parse())

