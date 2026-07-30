from aiogram.types import Message
from aiogram.filters import Command

from loader import dp
from config import ADMIN_ID
from services.users_store import get_admin_stats


@dp.message(Command("admin_stats"))
async def admin_stats(message: Message):
    if message.from_user.id != ADMIN_ID:
        return  # тихо игнорируем, если это не ты

    stats = get_admin_stats()

    await message.answer(
        "👤 Пользователи бота:\n\n"
        f"Всего зарегистрировано: {stats['total']}\n"
        f"Заходили сегодня: {stats['active_today']}\n"
        f"Заходили за 7 дней: {stats['active_7d']}"
    )


@dp.message(Command("myid"))
async def my_id(message: Message):
    await message.answer(f"Твой Telegram ID: {message.from_user.id}")