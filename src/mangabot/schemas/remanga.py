from pydantic import BaseModel, ConfigDict, model_validator
from mangabot.utils.text import normalize_for_search
from typing import Any

BASE_URL = "https://remanga.org"


class RawTitle(BaseModel):
    main_name: str
    dir: str
    cover: dict
    status: dict
    translate_status: dict
    is_erotic: bool



class RawChapter(BaseModel):
    id: int
    tome: int
    chapter: str
    title: RawTitle
    model_config = ConfigDict(extra="ignore")


class Remanga(BaseModel):
    id: int
    title: str
    search_title: str
    manga_url: str
    chapter_number: str
    chapter_url: str
    photo_url: str
    thumbnail_url: str
    is_adult: bool
    status: str
    translate_status: str
    source: str
    model_config = ConfigDict(extra="ignore")

    @model_validator(mode='before')
    @classmethod
    def buld_from_raw(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            raise ValueError("Ожидается словарь для преобразования")

        raw = RawChapter(**data)

        title = raw.title.main_name
        search_title = normalize_for_search(raw.title.main_name)
        manga_dir = raw.title.dir
        manga_url = f"{BASE_URL}/manga/{manga_dir}"
        chapter_number = f"Том {raw.tome} Глава {raw.chapter}"
        chapter_url = f"{manga_url}/{raw.id}" 
        photo_url = f"{BASE_URL}{raw.title.cover.get('high', raw.title.cover.get('mid', ''))}"
        thumbnail_url = f"{BASE_URL}{raw.title.cover.get('low', "")}"
        is_adult = raw.title.is_erotic
        status = raw.title.status.get("name", "")
        translate_status = raw.title.translate_status.get("name", "")
        source = "remanga"
        return {
            "id": raw.id,
            "title": title,
            "search_title": search_title,
            "manga_url": manga_url,
            "chapter_number": chapter_number,
            "chapter_url": chapter_url,
            "photo_url": photo_url,
            "thumbnail_url": thumbnail_url,
            "is_adult": is_adult,
            "status": status,
            "translate_status": translate_status,
            "source": source
        }
