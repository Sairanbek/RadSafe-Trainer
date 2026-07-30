from aiogram import F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from loader import dp
from services.db_repository import load_questions, get_sections


questions = load_questions()
sections = get_sections(questions)


def topics_keyboard():
    buttons = []

    for index, section in enumerate(sections):
        buttons.append(
            [
                InlineKeyboardButton(
                    text=section,
                    callback_data=f"topic:{index}"
                )
            ]
        )

    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )


@dp.message(F.text == "📚 Темы")
async def show_topics(message: Message):

    await message.answer(
        "📖 Выберите раздел обучения:",
        reply_markup=topics_keyboard()
    )


@dp.callback_query(F.data.startswith("topic:"))
async def topic_info(callback: CallbackQuery):

    index = int(callback.data.split(":")[1])

    section = sections[index]

    count = len(
        [
            q for q in questions
            if q.section == section
        ]
    )

    await callback.message.answer(
        f"📖 {section}\n\n"
        f"Количество вопросов: {count}\n\n"
        "В этом режиме можно изучать раздел отдельно."
    )

    await callback.answer()