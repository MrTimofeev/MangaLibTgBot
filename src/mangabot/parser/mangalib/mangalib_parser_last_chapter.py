# import asyncio
import json
import requests
import pprint
import httpx
import asyncio

from mangabot.models.mangalib_model import Mangalib
from pydantic import ValidationError
from mangabot.database.crud import save_manga_and_chapter
from mangabot.utils.text import normalize_for_search


HEADERS = {
    'accept': '*/*',
    'accept-language': 'ru-RU,ru;q=0.9',
    'client-time-zone': 'Europe/Moscow',
    'content-type': 'application/json',
    'dnt': '1',
    'origin': 'https://mangalib.me',
    'priority': 'u=1, i',
    'referer': 'https://mangalib.me/',
    'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'site-id': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
}

PARAMS = {
    'page': '1',
}


def sync_parse():
    response = requests.get(
        'https://api.cdnlibs.org/api/latest-updates', params=PARAMS, headers=HEADERS)

    result_dict = []
    try:
        data = json.loads(response.text)
        for item in data["data"]:
            _dict = {}

            _dict["Manga_name"] = item["rus_name"].lower()
            _dict["link_manga"] = f"https://mangalib.org/ru/manga/{item['slug_url']}"
            try:
                Volume = item["metadata"]["latest_items"]["items"][0]["volume"]
                Chapter = item["metadata"]["latest_items"]["items"][0]["number"]
            except:
                Volume = 1
                Chapter = 1

            _dict["new_chapter"] = f"Том {Volume} Глава {Chapter}"
            _dict["new_chapter_link"] = f"https://mangalib.org/ru/{item['slug_url']}/read/v{Volume}/c{Chapter}"

            _dict["photo_url"] = item["cover"]["default"]
            _dict["thumbnail_url"] = item["cover"]["thumbnail"]
            result_dict.append(_dict)

    except json.JSONDecodeError:
        print("Ошибка: данные не в формате JSON")
        data = None

    pprint.pprint(result_dict)

    return result_dict




async def new_chapter(bot):
    async with httpx.AsyncClient() as client:
        response = await client.get('https://api.cdnlibs.org/api/latest-updates', headers=HEADERS, params=PARAMS)

        data = response.json()

        for item in data["data"]:
            try:
                chapter = Mangalib(**item)
                await save_manga_and_chapter(
                    chapter.title,
                    search_title=normalize_for_search(chapter.title),
                    manga_url=chapter.manga_url,
                    chapter_number=chapter.chapter_number,
                    chapter_url=chapter.chapter_url,
                    photo_url=chapter.photo_url,
                    thumbnail_url=chapter.thumbnail_url,
                    source=chapter.source,
                    bot=bot
                )
            except ValidationError as e:
                print(f"Ошибка парсинга главы: {e}")
                continue
            
        print("Парсинг завершён и данные сохранены.")