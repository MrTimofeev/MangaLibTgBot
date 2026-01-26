from pydantic import BaseModel


class MangaSave(BaseModel):
    title: str
    search_title: str
    url: str
    last_chapter_number: str
    last_chapter_url: str
    photo_url: str
    thumbnail_url: str
    is_adult: bool
    status: str
    translate_status: str
    source: str
