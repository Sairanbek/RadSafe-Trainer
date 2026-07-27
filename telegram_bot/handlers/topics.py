from aiogram import F
from aiogram.types import Message

from loader import dp

from services.excel_loader import load_questions


questions = load_questions()


@dp.message(F.text == "📚 Темы")
async def topics(message: Message):

    await message.answer(
        f"☢ Радиационная безопасность\n\n"
        f"Всего вопросов: {len(questions)}\n\n"
        f"Скоро здесь появятся все темы."
    )