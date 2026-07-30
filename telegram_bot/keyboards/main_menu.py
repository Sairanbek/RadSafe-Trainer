from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Главное меню
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📝 Начать тест")],
        [KeyboardButton(text="🔁 Мои ошибки")],
        [KeyboardButton(text="📊 Моя статистика")],
        [KeyboardButton(text="🕓 История тестов")],
        [KeyboardButton(text="ℹ️ О программе")]
    ],
    resize_keyboard=True
)