import requests
import httpx
from mangabot.schemas.remanga import Remanga
from pydantic import ValidationError
import asyncio
from mangabot.utils.text import normalize_for_search
from mangabot.database.crud import save_manga
from mangabot.database.session import init_db
from mangabot.utils.text import clean_title
from mangabot.database.dto import MangaSave

import time
import random

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


def sync_pars():
    response = requests.get(
        'https://api.remanga.org/api/v2/search/catalog/https://api.remanga.org/api/v2/search/catalog/?count=30&page=1')

    pprint.pprint(response.json())


async def new_chapter():
    count = 500
    flag = True
    async with httpx.AsyncClient() as client:
        while flag:
            response = requests.get(
                f'https://api.remanga.org/api/v2/search/catalog/?count=30&page={count}&ordering=-score', headers=HEADERS)
            response.raise_for_status()
            # time.sleep(random.randint(2, 5))

            result_dict = []
            try:
                data = response.json()
                if count == 1000:
                    flag = False

                for item in data["results"]:
                    _dict = {}
                    if item["main_name"] == "" or item["main_name"] == None:
                        _dict["Manga_name"] = item["secondary_name"]
                    else:
                        _dict["Manga_name"] = item["main_name"]
                    title_name = clean_title(item['dir'])
                    _dict["link_manga"] = f"https://remanga.org/manga/{title_name}/main"
                    _dict["new_chapter"] = "Том 1 Глава 1"
                    _dict["new_chapter_link"] = f"https://remanga.org/manga/{title_name}/main"
                    _dict["photo_url"] = f"https://remanga.org{item["cover"]["high"]}" if len(
                        # TODO: У некоторых манхв нет картинки
                        item["cover"]) != 0 else ""
                    _dict["thumbnail_url"] = f"https://remanga.org/{item["cover"]["low"]}" if len(
                        item["cover"]) != 0 else ""

                    result_dict.append(_dict)
                    for manga_info in result_dict:
                        manga = MangaSave(
                            title=manga_info["Manga_name"],
                            search_title=normalize_for_search(
                                manga_info["Manga_name"]),
                            manga_url=manga_info["link_manga"],
                            chapter_number=manga_info["new_chapter"],
                            chapter_url=manga_info["new_chapter_link"],
                            photo_url=manga_info["photo_url"],
                            thumbnail_url=manga_info["thumbnail_url"],
                            source="remanga"
                        )

                        await save_manga(manga)

                print(
                    f"[INFO] Обработана {count} страница, количество тайтлов: {len(result_dict)}")
                count += 1
            except Exception as e:
                print(f"Ошибка при парсинге {e}")


async def on_startup():
    await init_db()


async def main() -> None:
    await on_startup()
    await new_chapter()


if __name__ == "__main__":
    # Запускаем основную функцию
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit) as e:
        print(f"Ошибка при завершении: {e}")


# TODO:Доделать полный парсинг пока он только делать запрос к 1 странице (из-за большого количества быстрых запросов он блочится)
