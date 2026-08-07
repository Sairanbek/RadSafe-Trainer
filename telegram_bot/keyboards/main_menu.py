from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="☢ Аттестация"),
            KeyboardButton(text="📝 Тренировка")
        ],
        [
            KeyboardButton(text="📚 Темы"),
            KeyboardButton(text="🔁 Мои ошибки")
        ],
        [
            KeyboardButton(text="📊 Моя статистика"),
            KeyboardButton(text="🕓 История тестов")
        ],
        [
            KeyboardButton(text="ℹ️ О программе")
        ]
    ],
    resize_keyboard=True
)