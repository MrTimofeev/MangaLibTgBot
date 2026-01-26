# import asyncio
import json
import requests
import pprint
import httpx
import asyncio

from mangabot.schemas.mangalib import Mangalib
from pydantic import ValidationError
from mangabot.database.crud import save_manga_and_chapter
from mangabot.utils.text import normalize_for_search
from mangabot.mappers.mangalib import mangalib_manga_to_dto

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

    data = response.json()

    for item in data["data"]:
        try:
            chapter = Mangalib(**item)
            pprint.pprint(chapter)
        except ValidationError as e:
            print(f"Ошибка парсинга главы: {e}")
            continue


async def new_chapter(bot):
    async with httpx.AsyncClient() as client:
        response = await client.get('https://api.cdnlibs.org/api/latest-updates', headers=HEADERS, params=PARAMS)

        data = response.json()

        for item in data["data"]:
            try:
                chapter = Mangalib(**item)
                dto_chapter = mangalib_manga_to_dto(chapter)
                await save_manga_and_chapter(
                    dto=dto_chapter,
                    bot=bot
                )
                pprint.pprint(dto_chapter.title)
            except ValidationError as e:
                print(f"Ошибка парсинга главы: {e}")
                continue

        print("Парсинг mangalib завершён и данные сохранены.")
        
        
