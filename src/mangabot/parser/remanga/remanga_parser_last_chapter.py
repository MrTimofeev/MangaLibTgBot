import requests
import httpx
from mangabot.schemas.remanga import Remanga
from pydantic import ValidationError
import asyncio
from mangabot.database.crud import save_manga_and_chapter
from mangabot.utils.text import normalize_for_search
from mangabot.mappers.remanga import remanga_manga_to_dto
import pprint

HEADERS = {
    'accept': '*/*',
    'accept-language': 'ru-RU,ru;q=0.9',
    'content-type': 'application/json',
    'dnt': '1',
    'origin': 'https://remanga.org',
    'priority': 'u=1, i',
    'referer': 'https://remanga.org/',
    'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
}

PARAMS = {
    'count': '20',
    'page': '1',
}


def sync_pars():
    response = requests.get(
        'https://api.remanga.org/api/v2/titles/last-chapters/', params=PARAMS, headers=HEADERS)

    data = response.json()

    for item in data["results"]:
        try:
            chapter = Remanga(**item)
            pprint.pprint(chapter)
        except ValidationError as e:
            print(f"Ошибка прасинга главы: {e}")
            continue


async def new_chapter(bot):
    async with httpx.AsyncClient() as client:
        response = await client.get('https://api.remanga.org/api/v2/titles/last-chapters/', headers=HEADERS, params=PARAMS)

        data = response.json()

        for item in data["results"]:
            try:
                chapter = Remanga(**item)
                dto_chapter = remanga_manga_to_dto(chapter)
                await save_manga_and_chapter(
                    dto_chapter,
                    bot=bot
                )
            except ValidationError as e:
                print(f"Ошибка парсинга главы:{e}")
                continue
        print("Парсинг remanga завершён и данные сохранены.")