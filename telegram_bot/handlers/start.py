from aiogram import F
from aiogram.types import Message
from aiogram.filters import CommandStart

from loader import dp

from aiogram.fsm.context import FSMContext

from states.user_state import UserRegistration

from database.db_repository import (
    get_user,
    create_user,
    get_progress,
    update_visit
)

from keyboards.main_menu import main_menu


@dp.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):

    user_id = message.from_user.id

    user = get_user(user_id)

    if user is None:
        await state.set_state(UserRegistration.waiting_name)

        await message.answer(
            "☢ Добро пожаловать в RST\n\n"
            "Radiation Safety Trainer\n\n"
            "Введите ваше имя:"
        )
        return

    update_visit(user_id)

    tests, average = get_progress(user_id)

    await message.answer(
        f"Здравствуйте, {user['first_name']}! 👋\n\n"
        f"Ваш прогресс:\n\n"
        f"📝 Пройдено тестов: {tests}\n"
        f"📊 Средний результат: {average}%\n",
        reply_markup=main_menu
    )


@dp.message(UserRegistration.waiting_name)
async def save_name(
        message: Message,
        state: FSMContext
):

    user_id = message.from_user.id

    create_user(
        user_id,
        message.text.strip(),
        message.from_user.username or ""
    )

    await state.clear()

    await message.answer(
        f"Здравствуйте, {message.text}! 👋\n\n"
        "Ваш профиль создан.\n\n"
        "Ваш прогресс:\n\n"
        "📝 Пройдено тестов: 0\n"
        "📊 Средний результат: 0%",
        reply_markup=main_menu
    )