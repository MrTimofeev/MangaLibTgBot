import asyncio
import time
import json
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from MangaBot.database.db import save_manga, init_db

# https://api.mangalib.me/api/manga/179033--a-super-villain-daily-life?fields[]=summary
# Вот запрос чтобы вытянуть описание у манги, там еще можно много чего вытянуть если знать фильтры

# Функция для запуска синхронного кода в асинхронном контексте
async def sync_parse():
    options = webdriver.ChromeOptions()

    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36')

    # Run in the background
    options.add_argument("--headless")

    s = Service(
        executable_path="D:\\python progect\\\Posting_vk_bot\\folder\\chromedriver.exe")
    driver = webdriver.Chrome(service=s, options=options)
    count = 698
    flag = True
    while flag:
        driver.get(url=f"https://api.mangalib.me/api/manga?page={count}")
        time.sleep(2)

        json_data = driver.find_element(By.TAG_NAME, 'pre')

        result_dict = []
        try:
            data = json.loads(json_data.text)
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
                _dict["new_chapter_link"] = "https://mangalib.org/ru/{item['slug_url']}/read/v1/c1"
                _dict["photo_url"] = item["cover"]["default"]
                _dict["thumbnail_url"] = item["cover"]["thumbnail"]

                result_dict.append(_dict)

            
                # Сохранение манги и глав в базу данных
            for manga_info in result_dict:
                title = manga_info["Manga_name"]
                manga_url = manga_info["link_manga"]
                chapter_number = manga_info["new_chapter"]  # Получаем номер главы
                chapter_url = manga_info["new_chapter_link"]
                photo_url = manga_info["photo_url"]
                thumbnail_url = manga_info["thumbnail_url"]

                await save_manga(title, manga_url, chapter_number, chapter_url, photo_url, thumbnail_url)

            print(f"[INFO] Обработана {count} страница")
            count += 1
        except json.JSONDecodeError:
            print("Ошибка: данные не в формате JSON")


    driver.close()
    driver.quit()

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