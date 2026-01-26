from mangabot.parser.mangalib.mangalib_parser_last_chapter import new_chapter as new_chapter_mangalib
from mangabot.parser.remanga.remanga_parser_last_chapter import new_chapter as new_chapter_remanga

async def check_new_chapters(bot):
    await new_chapter_mangalib(bot)
    await new_chapter_remanga(bot)
