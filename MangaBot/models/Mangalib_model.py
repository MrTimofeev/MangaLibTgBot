from pydantic import BaseModel, ConfigDict

class Mangalib(BaseModel):
    id: int
    title: str
    manga_url: str
    chapter_number: str
    chapter_url: str
    photo_url: str
    thumbnail_url: str
    
    model_config = ConfigDict(extra="ignore")
    
    