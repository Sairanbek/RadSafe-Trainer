from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

test_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="👁 Показать ответ")
        ],
        [
            KeyboardButton(text="➡ Следующий вопрос")
        ],
        [
            KeyboardButton(text="🏠 Главное меню")
        ]
    ],
    resize_keyboard=True
)