import asyncio
import handlers.menu

from loader import bot, dp
from aiogram.types import Message
from aiogram.filters import CommandStart
from keyboards.main_menu import main_menu


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "🛡 RST\n"
        "Radiation Safety Trainer\n\n"
        "Добро пожаловать!\n\n"
        "Тренажер предназначен для подготовки к аттестации специалистов в области:\n\n"
        "☢ Радиационной безопасности\n"
        "🩻 Рентгенологии\n"
        "🏥 Компьютерной томографии\n"
        "⚛ Ядерной медицины\n\n"
        "Выберите действие:",
        reply_markup=main_menu
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())