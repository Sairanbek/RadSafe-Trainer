import random
import time
import asyncio

from aiogram import F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton
)

from loader import dp, bot

from services.db_repository import load_questions, get_sections, get_subsections
from services.progress_store import (
    add_mistake,
    remove_mistake,
    get_mistake_ids
)
from services.stats_store import record_answer
from services.history_store import add_session
from utils.safe_answer import safe_answer

from keyboards.main_menu import main_menu


# =========================
# Загрузка вопросов
# =========================

all_questions = load_questions()
questions_by_id = {q.id: q for q in all_questions}
sections = get_sections(all_questions)


# =========================
# Настройки
# =========================

LETTERS = ["A", "B", "C", "D", "E"]

EXAM_QUESTIONS = 50
EXAM_TIME = 75 * 60


def get_training_length(section):
    if section == "ALL":
        return 50

    count = len([q for q in all_questions if q.section == section])

    if count <= 30:
        return count
    if count <= 100:
        return 30
    if count <= 200:
        return 40
    return 50


# =========================
# Состояние пользователей
# =========================

user_state = {}


# =========================
# Кнопка во время теста
# =========================

test_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🏠 Главное меню")]],
    resize_keyboard=True
)


# =========================
# Клавиатура разделов
# =========================

def section_keyboard():
    buttons = [[InlineKeyboardButton(text="🎲 Все разделы", callback_data="section:ALL")]]

    for index, section in enumerate(sections):
        buttons.append(
            [InlineKeyboardButton(text=section, callback_data=f"section:{index}")]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def subsection_keyboard(section, section_index):
    subs = get_subsections(all_questions, section)
    counts = {s: len([q for q in all_questions if q.section == section and q.subsection == s]) for s in subs}

    buttons = [[InlineKeyboardButton(
        text=f"🎲 Весь раздел ({len([q for q in all_questions if q.section == section])})",
        callback_data=f"subsection:{section_index}:ALL"
    )]]
    for sub_index, sub in enumerate(subs):
        buttons.append(
            [InlineKeyboardButton(text=f"{sub} ({counts[sub]})", callback_data=f"subsection:{section_index}:{sub_index}")]
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def section_has_useful_subsections(section):
    subs = get_subsections(all_questions, section)
    if len(subs) < 2:
        return False
    counts = [len([q for q in all_questions if q.section == section and q.subsection == s]) for s in subs]
    return sum(1 for c in counts if c >= 3) >= 2


# =========================
# Таймер
# =========================

def get_timer_text(state):
    if state.get("mode") != "exam":
        return ""

    passed = time.time() - state["start_time"]
    left = state["time_limit"] - passed

    if left <= 0:
        return "⏰ Время вышло"

    minutes = int(left // 60)
    seconds = int(left % 60)

    return f"⏱ Осталось: {minutes:02}:{seconds:02}"


# =========================
# Создание вопроса
# =========================

def build_question(user_id):
    state = user_state[user_id]

    if state["mode"] == "mistakes":
        pool = [questions_by_id[qid] for qid in state["pool_ids"] if qid in questions_by_id]
    else:
        candidates = all_questions
        if state["section"] != "ALL":
            candidates = [q for q in candidates if q.section == state["section"]]
        if state.get("subsection"):
            candidates = [q for q in candidates if q.subsection == state["subsection"]]
        pool = [q for q in candidates if q.id not in state["used"]]

    if not pool:
        return None, None

    q = random.choice(pool)

    state["current_qid"] = q.id
    state["used"].append(q.id)

    options = [q.answer] + q.wrong_answers[:4]
    random.shuffle(options)

    correct_letter = LETTERS[options.index(q.answer)]

    letter_map = {}
    buttons = []
    text_options = []

    for i, option in enumerate(options):
        letter = LETTERS[i]
        letter_map[letter] = option
        text_options.append(f"{letter}) {option}")
        buttons.append([InlineKeyboardButton(text=letter, callback_data=f"answer:{letter}")])

    state["correct_letter"] = correct_letter
    state["options_full"] = letter_map

    timer = get_timer_text(state)
    timer_block = f"{timer}\n\n" if timer else ""

    text = (
        f"📝 Вопрос {state['asked'] + 1} из {state['total']}\n\n"
        f"{timer_block}"
        f"{q.question}\n\n"
        + "\n".join(text_options)
    )

    return text, InlineKeyboardMarkup(inline_keyboard=buttons)


# =========================
# Итог теста
# =========================

def summary_text(state):
    total = state["total"]
    asked = state["asked"]
    correct = state["correct"]
    wrong = state["wrong"]
    unanswered = total - asked

    percent = round(correct / total * 100) if total else 0
    verdict = "✅ Сдал" if percent >= 70 else "❌ Не сдал"

    lines = [
        "🏁 Тест завершён!\n",
        f"📝 Отвечено: {asked} из {total}",
    ]

    if unanswered > 0:
        lines.append(f"⏳ Не отвечено (время вышло): {unanswered}")

    lines += [
        f"✅ Правильных: {correct}",
        f"❌ Ошибок: {wrong}",
        f"📊 Результат: {percent}% (от общего числа вопросов)\n",
        f"{verdict}",
        "Порог сдачи: 70%"
    ]

    return "\n".join(lines)


# =========================
# Тренировка
# =========================

@dp.message(F.text == "📝 Тренировка")
async def start_training(message: Message):
    await message.answer(
        "📝 Тренировка\n\n"
        "Выберите раздел:",
        reply_markup=section_keyboard()
    )


# =========================
# Аттестация
# =========================

@dp.message(F.text == "☢ Аттестация")
async def start_exam(message: Message):
    user_id = message.from_user.id

    user_state[user_id] = {
        "mode": "exam",
        "section": "ALL",
        "subsection": None,
        "total": EXAM_QUESTIONS,
        "asked": 0,
        "correct": 0,
        "wrong": 0,
        "used": [],
        "start_time": time.time(),
        "time_limit": EXAM_TIME
    }

    await message.answer(
        "☢ Аттестация начата!\n\n"
        "📝 Вопросов: 50\n"
        "⏱ Время: 75 минут\n\n"
        "Удачи!",
        reply_markup=test_menu
    )

    text, keyboard = build_question(user_id)
    await message.answer(text, reply_markup=keyboard)


# =========================
# Мои ошибки
# =========================

@dp.message(F.text == "🔁 Мои ошибки")
async def start_mistakes(message: Message):
    user_id = message.from_user.id
    mistakes = list(get_mistake_ids(user_id))

    if not mistakes:
        await message.answer("🎉 Ошибок нет!")
        return

    user_state[user_id] = {
        "mode": "mistakes",
        "pool_ids": mistakes,
        "section": "Ошибки",
        "subsection": None,
        "total": len(mistakes),
        "asked": 0,
        "correct": 0,
        "wrong": 0,
        "used": []
    }

    await message.answer("🔁 Повтор ошибок", reply_markup=test_menu)

    text, keyboard = build_question(user_id)
    await message.answer(text, reply_markup=keyboard)


# =========================
# Выбор раздела
# =========================

@dp.callback_query(F.data.startswith("section:"))
async def choose_section(callback: CallbackQuery):
    value = callback.data.split(":")[1]

    if value == "ALL":
        await start_training_session(callback, "ALL")
        return

    section_index = int(value)
    section = sections[section_index]

    if section_has_useful_subsections(section):
        await callback.message.answer(
            f"Раздел: {section}\n\nВыберите подраздел:",
            reply_markup=subsection_keyboard(section, section_index)
        )
        await safe_answer(callback)
        return

    await start_training_session(callback, section)


@dp.callback_query(F.data.startswith("subsection:"))
async def choose_subsection(callback: CallbackQuery):
    _, section_index, sub_value = callback.data.split(":")
    section = sections[int(section_index)]

    if sub_value == "ALL":
        await start_training_session(callback, section)
        return

    subs = get_subsections(all_questions, section)
    subsection = subs[int(sub_value)]
    await start_training_session(callback, section, subsection)


async def start_training_session(callback, section, subsection=None):
    user_id = callback.from_user.id

    if subsection:
        pool_size = len([q for q in all_questions if q.section == section and q.subsection == subsection])
        total = min(pool_size, 50)
    else:
        total = get_training_length(section)

    user_state[user_id] = {
        "mode": "training",
        "section": section,
        "subsection": subsection,
        "total": total,
        "asked": 0,
        "correct": 0,
        "wrong": 0,
        "used": []
    }

    label = f"{section} → {subsection}" if subsection else section
    await callback.message.answer(
        "📝 Тренировка начата\n\n"
        f"Раздел: {label}\n"
        f"Количество вопросов: {total}",
        reply_markup=test_menu
    )

    text, keyboard = build_question(user_id)
    await callback.message.answer(text, reply_markup=keyboard)
    await safe_answer(callback)


# =========================
# Автоматический таймер
# =========================

async def timer_checker():
    while True:
        await asyncio.sleep(10)

        now = time.time()

        for user_id, state in list(user_state.items()):
            if state.get("mode") != "exam":
                continue

            if now - state["start_time"] >= state["time_limit"]:
                await bot.send_message(
                    user_id,
                    "⏰ Время аттестации закончилось!\n\n" + summary_text(state)
                )
                await bot.send_message(
                    user_id,
                    "🏠 Главное меню",
                    reply_markup=main_menu
                )
                user_state.pop(user_id, None)


# =========================
# Проверка ответа
# =========================

@dp.callback_query(F.data.startswith("answer:"))
async def check_answer(callback: CallbackQuery):
    user_id = callback.from_user.id
    state = user_state.get(user_id)

    if not state:
        await safe_answer(callback, "Начните тест сначала", show_alert=True)
        return

    # проверка времени аттестации
    if state.get("mode") == "exam":
        if time.time() - state["start_time"] >= state["time_limit"]:
            await callback.message.answer("⏰ Время аттестации закончилось!")
            await callback.message.answer(summary_text(state))
            await callback.message.answer("🏠 Главное меню", reply_markup=main_menu)

            user_state.pop(user_id, None)
            await safe_answer(callback)
            return

    chosen = callback.data.split(":")[1]
    correct = state["correct_letter"]
    qid = state["current_qid"]
    question = questions_by_id[qid]

    if chosen == correct:
        state["correct"] += 1
        await callback.message.answer("✅ Верно!")
        record_answer(user_id, question.section, True)

        if state["mode"] == "mistakes":
            remove_mistake(user_id, qid)
    else:
        state["wrong"] += 1
        await callback.message.answer(
            "❌ Неверно.\n\n"
            f"Правильный ответ:\n"
            f"{state['options_full'][correct]}"
        )
        record_answer(user_id, question.section, False)
        add_mistake(user_id, qid)

    state["asked"] += 1
    await safe_answer(callback)

    # завершение теста
    if state["asked"] >= state["total"]:
        add_session(
            user_id,
            state["mode"],
            state.get("section", "ALL"),
            state["asked"],
            state["correct"],
            state["wrong"]
        )

        await callback.message.answer(summary_text(state))
        await callback.message.answer("🏠 Главное меню", reply_markup=main_menu)

        user_state.pop(user_id, None)
        return

    text, keyboard = build_question(user_id)

    if text is None:
        await callback.message.answer("Вопросы в этом разделе закончились 🎉")
        await callback.message.answer(summary_text(state))
        await callback.message.answer("🏠 Главное меню", reply_markup=main_menu)
        user_state.pop(user_id, None)
        return

    await callback.message.answer(text, reply_markup=keyboard)


# =========================
# Главное меню
# =========================

@dp.message(F.text == "🏠 Главное меню")
async def back_to_menu(message: Message):
    user_state.pop(message.from_user.id, None)
    await message.answer("🏠 Главное меню", reply_markup=main_menu)