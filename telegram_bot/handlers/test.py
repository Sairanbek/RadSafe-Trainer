import random

from aiogram import F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton
)

from loader import dp

from services.db_repository import load_questions, get_sections
from services.progress_store import add_mistake, remove_mistake, get_mistake_ids
from services.stats_store import record_answer
from services.history_store import add_session

from keyboards.main_menu import main_menu


# =========================
# Загрузка вопросов
# =========================

all_questions = load_questions()
questions_by_id = {q.id: q for q in all_questions}
sections = get_sections(all_questions)


# =========================
# Состояние пользователей
# =========================

user_state = {}

LETTERS = ["A", "B", "C", "D", "E"]
SESSION_LENGTH = 50

test_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🏠 Главное меню")]],
    resize_keyboard=True
)


# =========================
# Клавиатура разделов
# =========================

def section_keyboard():
    rows = [[InlineKeyboardButton(text="🎲 Все разделы", callback_data="section:ALL")]]
    for index, sec in enumerate(sections):
        rows.append([InlineKeyboardButton(text=sec, callback_data=f"section:{index}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# =========================
# Построение вопроса
# =========================

def build_question(user_id):
    state = user_state[user_id]

    if state["mode"] == "mistakes":
        pool = [questions_by_id[qid] for qid in state["pool_ids"] if qid in questions_by_id]
    else:
        if state["section"] == "ALL":
            pool = [q for q in all_questions if q.id not in state["used"]]
        else:
            pool = [
                q for q in all_questions
                if q.section == state["section"] and q.id not in state["used"]
            ]

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

    text = (
        f"📝 Вопрос {state['asked'] + 1} из {state['total']}\n\n"
        f"{q.question}\n\n"
        + "\n".join(text_options)
    )

    return text, InlineKeyboardMarkup(inline_keyboard=buttons)


# =========================
# Итог
# =========================

def summary_text(state):
    total = state["asked"]
    correct = state["correct"]
    wrong = state["wrong"]
    percent = round(correct / total * 100) if total else 0
    verdict = "✅ Сдал" if percent >= 70 else "❌ Не сдал"
    return (
        "🏁 Тест завершён!\n\n"
        f"Всего вопросов: {total}\n"
        f"✅ Правильных: {correct}\n"
        f"❌ Ошибок: {wrong}\n"
        f"Результат: {percent}%\n\n"
        f"{verdict}\n"
        "(порог 70%)"
    )


# =========================
# Начать тест
# =========================

@dp.message(F.text == "📝 Начать тест")
async def start_test(message: Message):
    await message.answer("Выберите раздел:", reply_markup=section_keyboard())


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
        "total": len(mistakes),
        "asked": 0,
        "correct": 0,
        "wrong": 0,
        "used": []
    }

    await message.answer("Повтор ошибок 👇", reply_markup=test_menu)
    text, keyboard = build_question(user_id)
    await message.answer(text, reply_markup=keyboard)


# =========================
# Выбор раздела
# =========================

@dp.callback_query(F.data.startswith("section:"))
async def choose_section(callback: CallbackQuery):
    user_id = callback.from_user.id
    value = callback.data.split(":")[1]
    section = "ALL" if value == "ALL" else sections[int(value)]

    user_state[user_id] = {
        "mode": "normal",
        "section": section,
        "total": SESSION_LENGTH,
        "asked": 0,
        "correct": 0,
        "wrong": 0,
        "used": []
    }

    await callback.message.answer("Тест начат 👇", reply_markup=test_menu)
    text, keyboard = build_question(user_id)
    await callback.message.answer(text, reply_markup=keyboard)
    await callback.answer()


# =========================
# Проверка ответа
# =========================

@dp.callback_query(F.data.startswith("answer:"))
async def check_answer(callback: CallbackQuery):
    user_id = callback.from_user.id
    state = user_state.get(user_id)

    if not state:
        await callback.answer("Начните тест сначала", show_alert=True)
        return

    chosen = callback.data.split(":")[1]
    correct = state["correct_letter"]
    qid = state["current_qid"]
    question = questions_by_id[qid]

    if chosen == correct:
        state["correct"] += 1
        chosen_text = state["options_full"][chosen]
        await callback.message.answer(f"✅ Верно! ({chosen}):\n{chosen_text}")
        record_answer(user_id, question.section, True)
        if state["mode"] == "mistakes":
            remove_mistake(user_id, qid)
    else:
        state["wrong"] += 1
        chosen_text = state["options_full"][chosen]
        correct_text = state["options_full"][correct]
        await callback.message.answer(
            f"❌ Неверно.\n\n"
            f"Вы выбрали ({chosen}):\n{chosen_text}\n\n"
            f"Правильный ответ ({correct}):\n{correct_text}"
        )
        record_answer(user_id, question.section, False)
        add_mistake(user_id, qid)

    state["asked"] += 1
    await callback.answer()

    if state["asked"] >= state["total"]:
        add_session(
            user_id,
            state["mode"],
            state.get("section", "Мои ошибки"),
            state["asked"],
            state["correct"],
            state["wrong"],
        )
        await callback.message.answer(summary_text(state))
        await callback.message.answer("🏠 Главное меню", reply_markup=main_menu)
        user_state.pop(user_id, None)
        return

    text, keyboard = build_question(user_id)

    if text is None:
        add_session(
            user_id,
            state["mode"],
            state.get("section", "Мои ошибки"),
            state["asked"],
            state["correct"],
            state["wrong"],
        )
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