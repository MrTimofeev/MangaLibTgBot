import requests
import httpx
from models.Remanga_model import Remanga
from pydantic import ValidationError
import asyncio

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

    response = requests.get('https://api.remanga.org/api/v2/titles/last-chapters/', params=PARAMS, headers=HEADERS)

    pprint.pprint(response.json())


async def new_chapter():
    async with httpx.AsyncClient() as client:
        response = await client.get('https://api.remanga.org/api/v2/titles/last-chapters/', headers=HEADERS, params=PARAMS)
        
        data = response.json()
        
        chapters = []
        
        for item in data["results"]:
            try:
                chapter = Remanga(**item)
                chapters.append(chapter)
                print(f"{chapter.title} - {chapter.chapter_number}")
            except ValidationError as e:
                print("Ошибка парсинга главы:")
                for err in e.errors():
                    print(f"  {err["loc"] - {err['msg']}}")
                continue
            
            

asyncio.run(new_chapter())