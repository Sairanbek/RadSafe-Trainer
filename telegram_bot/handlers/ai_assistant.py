from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

from loader import bot, dp
from services import ai_service
from services.history_store import get_history
from services.stats_store import get_stats
from states.user_state import AIChat
from keyboards.main_menu import main_menu

ai_chat_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🏠 Главное меню")]],
    resize_keyboard=True
)

# История чата в памяти процесса, по аналогии с user_state в handlers/test.py
chat_history: dict[int, list[dict]] = {}


@dp.message(F.text == "🤖 ИИ-ассистент")
async def start_ai_chat(message: Message, state: FSMContext):
    await state.set_state(AIChat.chatting)
    chat_history[message.from_user.id] = []
    await message.answer(
        "🤖 Спросите что-нибудь по радиационной безопасности или подготовке к аттестации.\n\n"
        "Чтобы выйти — нажмите «🏠 Главное меню».",
        reply_markup=ai_chat_menu
    )


@dp.message(F.text == "🧭 План обучения")
async def send_study_plan(message: Message):
    user_id = message.from_user.id
    stats = get_stats(user_id)

    if not stats:
        await message.answer("📊 Пока нет данных для плана. Пройдите хотя бы один тест!")
        return

    history = get_history(user_id, limit=50)

    await bot.send_chat_action(message.chat.id, "typing")
    try:
        text = await ai_service.study_plan(stats, history)
    except ai_service.GeminiError as e:
        await message.answer(f"⚠️ {e}")
        return

    await message.answer(f"🧭 Ваш план подготовки:\n\n{text}")


@dp.message(AIChat.chatting, F.text == "🏠 Главное меню")
async def exit_ai_chat(message: Message, state: FSMContext):
    await state.clear()
    chat_history.pop(message.from_user.id, None)
    await message.answer("🏠 Главное меню", reply_markup=main_menu)


@dp.message(AIChat.chatting)
async def ai_chat(message: Message):
    user_id = message.from_user.id
    text = (message.text or "").strip()
    if not text:
        return

    history = chat_history.setdefault(user_id, [])

    await bot.send_chat_action(message.chat.id, "typing")
    try:
        reply = await ai_service.chat_reply(history, text)
    except ai_service.GeminiError as e:
        await message.answer(f"⚠️ {e}")
        return

    history.append({"role": "user", "text": text})
    history.append({"role": "model", "text": reply})
    del history[:-20]

    await message.answer(reply)
