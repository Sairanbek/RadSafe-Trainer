from aiogram import F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from loader import dp
from services.db_repository import load_questions, get_sections, get_subsections
from utils.safe_answer import safe_answer

questions = load_questions()
sections = get_sections(questions)

browse_state = {}


def get_pool(section, subsection=None):
    pool = [q for q in questions if q.section == section]
    if subsection:
        pool = [q for q in pool if q.subsection == subsection]
    return pool


def section_has_useful_subsections(section):
    subs = get_subsections(questions, section)
    if len(subs) < 2:
        return False
    counts = [len(get_pool(section, s)) for s in subs]
    return sum(1 for c in counts if c >= 3) >= 2


def topics_keyboard():
    buttons = []
    for index, section in enumerate(sections):
        count = len(get_pool(section))
        buttons.append(
            [InlineKeyboardButton(text=f"{section} ({count})", callback_data=f"topic:{index}")]
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def subtopics_keyboard(section, section_index):
    subs = get_subsections(questions, section)
    buttons = [[InlineKeyboardButton(
        text=f"🎲 Весь раздел ({len(get_pool(section))})",
        callback_data=f"subtopic:{section_index}:ALL"
    )]]
    for sub_index, sub in enumerate(subs):
        count = len(get_pool(section, sub))
        buttons.append(
            [InlineKeyboardButton(text=f"{sub} ({count})", callback_data=f"subtopic:{section_index}:{sub_index}")]
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def browse_keyboard(position, total):
    row = []
    if position > 0:
        row.append(InlineKeyboardButton(text="◀️ Пред", callback_data="browse:prev"))
    row.append(InlineKeyboardButton(text=f"{position + 1}/{total}", callback_data="browse:noop"))
    if position < total - 1:
        row.append(InlineKeyboardButton(text="След ▶️", callback_data="browse:next"))
    return InlineKeyboardMarkup(inline_keyboard=[
        row,
        [InlineKeyboardButton(text="📚 Другой раздел", callback_data="browse:sections")]
    ])


def build_browse_text(section, subsection, position):
    pool = get_pool(section, subsection)
    q = pool[position]
    label = f"{section} → {subsection}" if subsection else section
    return f"📚 {label}\n\nВопрос {position + 1}:\n{q.question}\n\n💡 Ответ:\n{q.answer}"


@dp.message(F.text == "📚 Темы")
async def show_topics(message: Message):
    await message.answer("📚 Выберите раздел обучения:", reply_markup=topics_keyboard())


@dp.callback_query(F.data.startswith("topic:"))
async def topic_selected(callback: CallbackQuery):
    section_index = int(callback.data.split(":")[1])
    section = sections[section_index]

    if section_has_useful_subsections(section):
        await callback.message.answer(
            f"Раздел: {section}\n\nВыберите подраздел:",
            reply_markup=subtopics_keyboard(section, section_index)
        )
        await safe_answer(callback)
        return

    await open_browse(callback, section, None)


@dp.callback_query(F.data.startswith("subtopic:"))
async def subtopic_selected(callback: CallbackQuery):
    _, section_index, sub_value = callback.data.split(":")
    section = sections[int(section_index)]

    subsection = None
    if sub_value != "ALL":
        subs = get_subsections(questions, section)
        subsection = subs[int(sub_value)]

    await open_browse(callback, section, subsection)


async def open_browse(callback, section, subsection):
    user_id = callback.from_user.id
    browse_state[user_id] = {"section": section, "subsection": subsection, "position": 0}

    total = len(get_pool(section, subsection))
    text = build_browse_text(section, subsection, 0)
    await callback.message.answer(text, reply_markup=browse_keyboard(0, total))
    await safe_answer(callback)


@dp.callback_query(F.data == "browse:next")
async def browse_next(callback: CallbackQuery):
    user_id = callback.from_user.id
    state = browse_state.get(user_id)
    if not state:
        await safe_answer(callback, "Сначала выберите раздел", show_alert=True)
        return

    total = len(get_pool(state["section"], state["subsection"]))
    state["position"] = min(state["position"] + 1, total - 1)

    text = build_browse_text(state["section"], state["subsection"], state["position"])
    await callback.message.edit_text(text, reply_markup=browse_keyboard(state["position"], total))
    await safe_answer(callback)


@dp.callback_query(F.data == "browse:prev")
async def browse_prev(callback: CallbackQuery):
    user_id = callback.from_user.id
    state = browse_state.get(user_id)
    if not state:
        await safe_answer(callback, "Сначала выберите раздел", show_alert=True)
        return

    total = len(get_pool(state["section"], state["subsection"]))
    state["position"] = max(state["position"] - 1, 0)

    text = build_browse_text(state["section"], state["subsection"], state["position"])
    await callback.message.edit_text(text, reply_markup=browse_keyboard(state["position"], total))
    await safe_answer(callback)


@dp.callback_query(F.data == "browse:sections")
async def browse_back_to_sections(callback: CallbackQuery):
    user_id = callback.from_user.id
    browse_state.pop(user_id, None)
    await callback.message.answer("📚 Выберите раздел обучения:", reply_markup=topics_keyboard())
    await safe_answer(callback)


@dp.callback_query(F.data == "browse:noop")
async def browse_noop(callback: CallbackQuery):
    await safe_answer(callback)