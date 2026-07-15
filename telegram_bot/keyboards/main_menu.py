from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Главное меню
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📝 Начать тест")],
        [KeyboardButton(text="📚 Темы")],
        [KeyboardButton(text="📊 Моя статистика")],
        [KeyboardButton(text="ℹ️ О программе")]
    ],
    resize_keyboard=True
)

# Меню во время прохождения теста
test_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="👁 Показать ответ"),
            KeyboardButton(text="➡ Следующий вопрос")
        ],
        [
            KeyboardButton(text="🏠 Главное меню")
        ]
    ],
    resize_keyboard=True
)