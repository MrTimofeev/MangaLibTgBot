import asyncio
import time
import json
import random
import requests
from mangabot.utils.text import normalize_for_search
from mangabot.database.crud import save_manga
from mangabot.database.session import init_db
from mangabot.database.dto import MangaSave
# https://api.mangalib.me/api/manga/179033--a-super-villain-daily-life?fields[]=summary
# Вот запрос чтобы вытянуть описание у манги, там еще можно много чего вытянуть если знать фильтры

# Функция для запуска синхронного кода в асинхронном контексте


async def sync_parse():
    # headers = {
    #     'accept': '*/*',
    #     'accept-language': 'ru-RU,ru;q=0.9',
    #     'client-time-zone': 'Europe/Moscow',
    #     'content-type': 'application/json',
    #     'dnt': '1',
    #     'origin': 'https://mangalib.org',
    #     'priority': 'u=1, i',
    #     'referer': 'https://mangalib.org/',
    #     'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    #     'sec-ch-ua-mobile': '?0',
    #     'sec-ch-ua-platform': '"Windows"',
    #     'sec-fetch-dest': 'empty',
    #     'sec-fetch-mode': 'cors',
    #     'sec-fetch-site': 'cross-site',
    #     'site-id': '1',
    #     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
    # }

    count = 18
    flag = True
    while flag:
        response = requests.get(
            f'https://api.cdnlibs.org/api/manga?page={count}&site_id[]=1')
        response.raise_for_status()
        time.sleep(random.randint(10, 15))

        result_dict = []
        try:
            data = response.json()
            if data["meta"]["has_next_page"] == False:
                flag = False

            for item in data["data"]:
                _dict = {}
                if item["rus_name"] == "" or item["rus_name"] == None:
                    _dict["Manga_name"] = item["name"].lower()
                else:
                    _dict["Manga_name"] = item["rus_name"].lower()

                _dict["link_manga"] = f"https://mangalib.org/ru/manga/{item['slug_url']}"
                _dict["new_chapter"] = "Том 1 Глава 1"
                _dict["new_chapter_link"] = f"https://mangalib.org/ru/{item['slug_url']}/read/v1/c1"
                _dict["photo_url"] = item["cover"]["default"]
                _dict["thumbnail_url"] = item["cover"]["thumbnail"]

                result_dict.append(_dict)

                # Сохранение манги и глав в базу данных
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
                    source="mangalib"
                )

                await save_manga(manga)

            print(f"[INFO] Обработана {count} страница")
            count += 1
        except json.JSONDecodeError:
            print("Ошибка: данные не в формате JSON")


async def on_startup():
    await init_db()


async def main() -> None:
    await on_startup()
    await sync_parse()


if __name__ == "__main__":
    # Запускаем основную функцию
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit) as e:
        print(f"Ошибка при завершении: {e}")
