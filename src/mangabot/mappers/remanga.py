from mangabot.schemas.remanga import Remanga
from mangabot.database.dto import MangaSave


def remanga_manga_to_dto(manga: Remanga) -> MangaSave:
    return MangaSave(
       title=manga.title,
       search_title=manga.search_title,
       url=manga.manga_url,
       last_chapter_number=manga.chapter_number,
       last_chapter_url=manga.chapter_url,
       photo_url=manga.photo_url,
       thumbnail_url=manga.thumbnail_url,
       is_adult=manga.is_adult,
       status=manga.status,
       translate_status=manga.translate_status,
       source=manga.source
    )