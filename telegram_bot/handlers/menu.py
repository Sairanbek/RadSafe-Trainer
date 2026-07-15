from aiogram import F
from aiogram.types import Message

from loader import dp


from random import choice
from services.excel_loader import load_questions


from services.excel_loader import load_questions

questions = load_questions(
    "../questions/radiation_safety/Перечень тестов для аттестации по РБ.xlsx"
)


@dp.message(F.text == "📝 Начать тест")
async def start_test(message: Message):

    question = questions[0]

    await message.answer(
        f"Вопрос №{question.id}\n\n{question.question}"
    )


@dp.message(F.text == "📚 Темы")
async def themes(message: Message):
    await message.answer("📚 Здесь позже появятся темы для изучения.")


@dp.message(F.text == "📊 Моя статистика")
async def statistics(message: Message):
    await message.answer("📊 Пока статистика отсутствует.")


@dp.message(F.text == "ℹ️ О программе")
async def about(message: Message):
    await message.answer(
        "🛡 RST\n"
        "Radiation Safety Trainer\n\n"
        "Версия: 0.1\n"
        "Разработка: Сайранбек Бурабаев"
    )