from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📝 Начать тест")],
        [KeyboardButton(text="📚 Темы")],
        [KeyboardButton(text="📊 Моя статистика")],
        [KeyboardButton(text="ℹ️ О программе")]
    ],
    resize_keyboard=True
)