from pydantic import BaseModel, ConfigDict, model_validator
from typing import Any, List

BASE_URL = "https://mangalib.org"


class LatestChapterItem(BaseModel):
    id: int
    volume: str  # часто приходит как строка "1", "0", "1.5" — не int!
    number: str

class LatestItems(BaseModel):
    items: List[LatestChapterItem]

class Metadata(BaseModel):
    latest_items: LatestItems

class RawTitle(BaseModel):
    rus_name: str
    slug_url: str
    cover: dict

class RawManga(BaseModel):
    id: int
    rus_name: str
    slug_url: str
    cover: dict
    metadata: Metadata

    model_config = ConfigDict(extra="ignore")


class Mangalib(BaseModel):
    id: int
    title: str
    manga_url: str
    chapter_number: str
    chapter_url: str
    photo_url: str
    thumbnail_url: str
    
    model_config = ConfigDict(extra="ignore")

    @model_validator(mode='before')
    @classmethod
    def buld_from_raw(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            raise ValueError("Ожидается словарь")

        raw = RawManga(**data)
        
        
        latest_items = raw.metadata.latest_items.items
        
        if not latest_items:
            raise ValueError("Нет данных о последней главе в metadata.latest_items.items")
        
        
        last_chapter = latest_items[0]

        title = raw.rus_name
        manga_url = f"{BASE_URL}/ru/manga/{raw.slug_url}"
        chapter_number = f"Том {last_chapter.volume} Глава {last_chapter.number}"
        chapter_url = f"{BASE_URL}/ru/{raw.slug_url}/read/v{last_chapter.volume}/c{last_chapter.number}"
        photo_url = f"{raw.cover.get('default', "")}"
        thumbnail_url = f"{raw.cover.get('thumbnail', "")}"

        return {
            "id": raw.id,
            "title": title,
            "manga_url": manga_url,
            "chapter_number": chapter_number,
            "chapter_url": chapter_url,
            "photo_url": photo_url,
            "thumbnail_url": thumbnail_url
        }

    