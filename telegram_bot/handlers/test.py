from aiogram import F
from aiogram.types import Message

from loader import dp
from services.excel_loader import load_questions

questions = load_questions(
    "../questions/radiation_safety/Перечень тестов для аттестации по РБ.xlsx"
)


@dp.message(F.text == "📝 Начать тест")
async def start_test(message: Message):

    question = questions[0]

    await message.answer(
        f"📝 Вопрос 1 из {len(questions)}\n\n"
        f"{question.question}"
    )