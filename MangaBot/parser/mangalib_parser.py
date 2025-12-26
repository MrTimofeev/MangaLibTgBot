# import asyncio
import os
import time
import json
import requests
import pprint

# import asyncio

# from concurrent.futures import ThreadPoolExecutor
# from MangaBot.database.db import save_manga_and_chapter

# https://api.mangalib.me/api/manga/179033--a-super-villain-daily-life?fields[]=summary
# Вот запрос чтобы вытянуть описание у манги, там еще можно много чего вытянуть если знать фильтры

# Функция для запуска синхронного кода в асинхронном контексте


def sync_parse():
    headers = {
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

    params = {
        'page': '1',
    }
    response = requests.get(
        'https://api.cdnlibs.org/api/latest-updates', params=params, headers=headers)

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


sync_parse()


# # Асинхронная обертка для функции парсинга
# async def parse_manga(bot):
#     loop = asyncio.get_running_loop()

#     # Используем ThreadPoolExecutor для запуска синхронной функции
#     with ThreadPoolExecutor() as pool:
#         result_dict = await loop.run_in_executor(pool, sync_parse)

#      # Сохранение манги и глав в базу данных
#     for manga_info in result_dict:
#         title = manga_info["Manga_name"]
#         manga_url = manga_info["link_manga"]
#         chapter_number = manga_info["new_chapter"]  # Получаем номер главы
#         chapter_url = manga_info["new_chapter_link"]
#         photo_url = manga_info["photo_url"]
#         thumbnail_url = manga_info["thumbnail_url"]

#         await save_manga_and_chapter(title, manga_url, chapter_number, chapter_url, photo_url, thumbnail_url, bot)

#     print("Парсинг завершён и данные сохранены.")
