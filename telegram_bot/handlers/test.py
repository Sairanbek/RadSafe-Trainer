import random

from aiogram import F
from aiogram.types import Message

from loader import dp
from services.excel_loader import load_questions
from keyboards.main_menu import main_menu, test_menu

questions = load_questions()

current_question = None


@dp.message(F.text == "📝 Начать тест")
async def start_test(message: Message):
    global current_question

    current_question = random.choice(questions)

    await message.answer(
        f"📝 Вопрос\n\n"
        f"{current_question.question}",
        reply_markup=test_menu
    )


@dp.message(F.text == "👁 Показать ответ")
async def show_answer(message: Message):
    global current_question

    if current_question is None:
        await message.answer("Сначала начните тест.")
        return

    await message.answer(
        f"👁 Правильный ответ:\n\n"
        f"{current_question.answer}"
    )


@dp.message(F.text == "➡ Следующий вопрос")
async def next_question(message: Message):
    global current_question

    current_question = random.choice(questions)

    await message.answer(
        f"📝 Вопрос\n\n"
        f"{current_question.question}",
        reply_markup=test_menu
    )


@dp.message(F.text == "🏠 Главное меню")
async def back_to_menu(message: Message):
    global current_question

    current_question = None

    await message.answer(
        "🏠 Главное меню",
        reply_markup=main_menu
    )