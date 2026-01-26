import asyncio
import uuid
from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from mangabot.messages.templates import message_manga
from mangabot.bot.keyboards.inline import subscribe_keyboard
from mangabot.database.crud import get_manga, get_or_create_user
from mangabot.bot.config import SOURCES

router = Router()

@router.inline_query()
async def inline_search(query: InlineQuery):
    search_text = query.query.lower().strip()  # Убираем лишние пробелы
    if not search_text:
        return await query.answer([], cache_time=60)

    user = await get_or_create_user(query.from_user.id, query.from_user.full_name)
    
    if user.preferred_source is not None:
        preferred_sources = user.sources_list
    else:
        preferred_sources = [k for k, v in SOURCES.items() if v.get('enable', True)] 
    
    exclude_adult = not user.age_verifed
    
    try:
        manga_list = await asyncio.wait_for(
            get_manga(search_text, preferred_sources, exclude_adult),
            timeout=5
        )
    except asyncio.TimeoutError:
        return await query.answer([], cache_time=60)
    
    results = []
    for manga in manga_list[:40]:  # Ограничение уже должно быть в get_manga
        result_id = str(uuid.uuid4())
        message_content = message_manga(
            manga.title,
            manga.source,
            manga.photo_url, 
            manga.url
        )
        results.append(
            InlineQueryResultArticle(
                id=result_id,
                title=manga.title,
                description=f'{"Ограничение: 18+" if manga.is_adult else ""}\n{manga.source}',
                input_message_content=InputTextMessageContent(
                    message_text=message_content,
                    parse_mode="HTML"
                ),
                thumbnail_url=manga.thumbnail_url,
                thumbnail_width=400,
                thumbnail_height=400,
                reply_markup=subscribe_keyboard(manga.id)
            )
        )
        
    await query.answer(results, cache_time=60, is_personal=True)