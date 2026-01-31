from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from mangabot.bot.config import SOURCES
from mangabot.database.crud import set_age_verified, set_preferred_sources, get_or_create_user

router = Router()

@router.message(lambda msg: msg.text == "🔞 Подтвердить возраст")
async def cmd_age(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да, мне 18+",
                              callback_data="age_confirm")]
    ])
    await message.answer(
        "🔞 Этот бот может содержать контент для взрослых.\n"
        "Подтвердите, что вам исполнилось 18 лет.",
        reply_markup=kb
    )


@router.callback_query(lambda c: c.data == "age_confirm")
async def confirm_age(callback: types.CallbackQuery):
    await set_age_verified(callback.from_user.id, True)
    await callback.message.edit_text("✅ Возраст подтверждён. Вам доступен 18+ контент.")
    await callback.answer()


def make_sources_kb(selected: set[str]) -> InlineKeyboardMarkup:
    buttons = []
    for key, info in SOURCES.items():
        if not info.get("enabled", True):
            continue
        mark = "✅" if key in selected else "❌"
        name = info.get('name', key)
        buttons.append([InlineKeyboardButton(text=f"{mark} {name}", callback_data=f"src_{key}")])
    buttons.append([InlineKeyboardButton(text="Готово", callback_data="src_save")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(lambda msg: msg.text == "⚙️ Настройки источников")
async def cmd_sources(message: types.Message):
    user = await get_or_create_user(message.from_user.id, message.from_user.full_name)

    if user.sources_list is None:
        current = {k for k, v in SOURCES.items() if v.get("enabled", True)}
    else:
        current = set(user.sources_list)

    await message.answer(
        "Выберите источники для поиска:",
        reply_markup=make_sources_kb(current)
    )


@router.callback_query(lambda c: c.data.startswith("src_"))
async def handle_source_choice(callback: types.CallbackQuery):
    user = await get_or_create_user(callback.from_user.id, callback.from_user.full_name)

    current = set(user.sources_list or list(SOURCES.keys()))
    new_current = current.copy()

    source = callback.data

    if source == "src_save":
        await callback.message.edit_text("✅ Настройки источников сохранены!")
        await callback.answer()
        return
    else:
        if source.replace("src_", "") in new_current:
            new_current.remove(source.replace("src_", ""))
        else:
            new_current.add(source.replace("src_", ""))
        
        if not new_current:
            await callback.answer("Нужен хотя бы один источник", show_alert=True)
            return
        
        await set_preferred_sources(callback.from_user.id, list(new_current) if new_current else None)

        await callback.message.edit_reply_markup(reply_markup=make_sources_kb(new_current))
        await callback.answer()
