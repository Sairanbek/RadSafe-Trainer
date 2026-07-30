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

from services.db_repository import load_questions, get_sections
from services.progress_store import (
    add_mistake,
    remove_mistake,
    get_mistake_ids
)
from services.stats_store import record_answer
from services.history_store import add_session

from keyboards.main_menu import main_menu


# =========================
# Загрузка вопросов
# =========================

all_questions = load_questions()

questions_by_id = {
    q.id: q for q in all_questions
}

sections = get_sections(all_questions)


# =========================
# Настройки
# =========================

LETTERS = [
    "A",
    "B",
    "C",
    "D",
    "E"
]


EXAM_QUESTIONS = 50
EXAM_TIME = 75 * 60


def get_training_length(section):

    if section == "ALL":
        return 50

    count = len(
        [
            q for q in all_questions
            if q.section == section
        ]
    )

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
    keyboard=[
        [
            KeyboardButton(
                text="🏠 Главное меню"
            )
        ]
    ],
    resize_keyboard=True
)


# =========================
# Клавиатура разделов
# =========================

def section_keyboard():

    buttons = [
        [
            InlineKeyboardButton(
                text="🎲 Все разделы",
                callback_data="section:ALL"
            )
        ]
    ]

    for index, section in enumerate(sections):

        buttons.append(
            [
                InlineKeyboardButton(
                    text=section,
                    callback_data=f"section:{index}"
                )
            ]
        )

    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )


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

        pool = [
            questions_by_id[qid]
            for qid in state["pool_ids"]
            if qid in questions_by_id
        ]

    else:

        if state["section"] == "ALL":

            pool = [
                q for q in all_questions
                if q.id not in state["used"]
            ]

        else:

            pool = [
                q for q in all_questions
                if q.section == state["section"]
                and q.id not in state["used"]
            ]


    if not pool:
        return None, None


    q = random.choice(pool)


    state["current_qid"] = q.id

    state["used"].append(q.id)


    options = [
        q.answer
    ] + q.wrong_answers[:4]


    random.shuffle(options)


    correct_letter = LETTERS[
        options.index(q.answer)
    ]


    letter_map = {}

    buttons = []

    text_options = []


    for i, option in enumerate(options):

        letter = LETTERS[i]

        letter_map[letter] = option

        text_options.append(
            f"{letter}) {option}"
        )

        buttons.append(
            [
                InlineKeyboardButton(
                    text=letter,
                    callback_data=f"answer:{letter}"
                )
            ]
        )


    state["correct_letter"] = correct_letter

    state["options_full"] = letter_map


    timer = get_timer_text(state)


    text = (
        f"📝 Вопрос {state['asked'] + 1} "
        f"из {state['total']}\n\n"
        f"{timer}\n\n"
        f"{q.question}\n\n"
        + "\n".join(text_options)
    )


    return (
        text,
        InlineKeyboardMarkup(
            inline_keyboard=buttons
        )
    )
# =========================
# Итог теста
# =========================

def summary_text(state):

    total = state["asked"]
    correct = state["correct"]
    wrong = state["wrong"]

    percent = (
        round(correct / total * 100)
        if total else 0
    )

    verdict = (
        "✅ Сдал"
        if percent >= 70
        else "❌ Не сдал"
    )

    return (
        "🏁 Тест завершён!\n\n"
        f"📝 Всего вопросов: {total}\n"
        f"✅ Правильных: {correct}\n"
        f"❌ Ошибок: {wrong}\n"
        f"📊 Результат: {percent}%\n\n"
        f"{verdict}\n"
        "Порог сдачи: 70%"
    )


# =========================
# Тренировка
# =========================

@dp.message(F.text == "📝 Тренировка")
async def start_training(message: Message):

    await message.answer(
        "📚 Тренировка\n\n"
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


    await message.answer(
        text,
        reply_markup=keyboard
    )


# =========================
# Мои ошибки
# =========================

@dp.message(F.text == "🔁 Мои ошибки")
async def start_mistakes(message: Message):

    user_id = message.from_user.id


    mistakes = list(
        get_mistake_ids(user_id)
    )


    if not mistakes:

        await message.answer(
            "🎉 Ошибок нет!"
        )

        return


    user_state[user_id] = {

        "mode": "mistakes",

        "pool_ids": mistakes,

        "section": "Ошибки",

        "total": len(mistakes),

        "asked": 0,

        "correct": 0,

        "wrong": 0,

        "used": []
    }


    await message.answer(
        "🔁 Повтор ошибок",
        reply_markup=test_menu
    )


    text, keyboard = build_question(user_id)


    await message.answer(
        text,
        reply_markup=keyboard
    )


# =========================
# Выбор раздела
# =========================

@dp.callback_query(F.data.startswith("section:"))
async def choose_section(callback: CallbackQuery):

    user_id = callback.from_user.id


    value = callback.data.split(":")[1]


    if value == "ALL":

        section = "ALL"

    else:

        section = sections[int(value)]


    total = get_training_length(section)


    user_state[user_id] = {

        "mode": "training",

        "section": section,

        "total": total,

        "asked": 0,

        "correct": 0,

        "wrong": 0,

        "used": []
    }


    await callback.message.answer(
        "📚 Тренировка начата\n\n"
        f"Раздел: {section}\n"
        f"Количество вопросов: {total}",
        reply_markup=test_menu
    )


    text, keyboard = build_question(user_id)


    await callback.message.answer(
        text,
        reply_markup=keyboard
    )


    await callback.answer()


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
                    "⏰ Время аттестации закончилось!\n\n"
                    + summary_text(state)
                )


                await bot.send_message(
                    user_id,
                    "🏠 Главное меню",
                    reply_markup=main_menu
                )


                user_state.pop(
                    user_id,
                    None
                )
                # =========================
# Проверка ответа
# =========================

@dp.callback_query(F.data.startswith("answer:"))
async def check_answer(callback: CallbackQuery):

    user_id = callback.from_user.id

    state = user_state.get(user_id)


    if not state:

        await callback.answer(
            "Начните тест сначала",
            show_alert=True
        )

        return


    # проверка времени аттестации

    if state.get("mode") == "exam":

        if time.time() - state["start_time"] >= state["time_limit"]:

            await callback.message.answer(
                "⏰ Время аттестации закончилось!"
            )

            await callback.message.answer(
                summary_text(state)
            )

            await callback.message.answer(
                "🏠 Главное меню",
                reply_markup=main_menu
            )

            user_state.pop(
                user_id,
                None
            )

            await callback.answer()

            return


    chosen = callback.data.split(":")[1]


    correct = state["correct_letter"]

    qid = state["current_qid"]

    question = questions_by_id[qid]


    if chosen == correct:

        state["correct"] += 1


        await callback.message.answer(
            "✅ Верно!"
        )


        record_answer(
            user_id,
            question.section,
            True
        )


        if state["mode"] == "mistakes":

            remove_mistake(
                user_id,
                qid
            )


    else:

        state["wrong"] += 1


        await callback.message.answer(
            "❌ Неверно.\n\n"
            f"Правильный ответ:\n"
            f"{state['options_full'][correct]}"
        )


        record_answer(
            user_id,
            question.section,
            False
        )


        add_mistake(
            user_id,
            qid
        )


    state["asked"] += 1


    await callback.answer()



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


        await callback.message.answer(
            summary_text(state)
        )


        await callback.message.answer(
            "🏠 Главное меню",
            reply_markup=main_menu
        )


        user_state.pop(
            user_id,
            None
        )

        return



    text, keyboard = build_question(user_id)


    await callback.message.answer(
        text,
        reply_markup=keyboard
    )



# =========================
# Главное меню
# =========================

@dp.message(F.text == "🏠 Главное меню")
async def back_to_menu(message: Message):

    user_state.pop(
        message.from_user.id,
        None
    )


    await message.answer(
        "🏠 Главное меню",
        reply_markup=main_menu
    )