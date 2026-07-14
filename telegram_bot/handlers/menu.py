from aiogram import F
from aiogram.types import Message

from loader import dp


@dp.message(F.text == "📝 Начать тест")
async def start_test(message: Message):
    await message.answer("🚧 Раздел тестирования находится в разработке.")


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