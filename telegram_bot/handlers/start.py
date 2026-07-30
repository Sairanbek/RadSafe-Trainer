from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from states.registration import Registration
from database.db_repository import get_user, create_user, get_user_progress


router = Router()


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):

    telegram_id = message.from_user.id

    user = await get_user(telegram_id)

    if user:
        progress = await get_user_progress(telegram_id)

        await message.answer(
            f"Здравствуйте, {user.name}! ☢\n\n"
            f"Ваш прогресс:\n\n"
            f"📝 Пройдено тестов: {progress['tests']}\n"
            f"📊 Средний результат: {progress['average']}%"
        )

    else:
        await message.answer(
            "☢ Добро пожаловать в RST!\n\n"
            "Для начала подготовки введите ваше имя:"
        )

        await state.set_state(Registration.waiting_name)


@router.message(Registration.waiting_name)
async def save_name(message: Message, state: FSMContext):

    name = message.text.strip()

    await create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        name=name
    )

    await state.clear()

    await message.answer(
        f"Здравствуйте, {name}! 👋\n\n"
        "Вы зарегистрированы в Radiation Safety Trainer.\n\n"
        "Ваш прогресс:\n\n"
        "📝 Пройдено тестов: 0\n"
        "📊 Средний результат: 0%"
    )