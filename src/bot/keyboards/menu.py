from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Добавить напоминание")],
            [KeyboardButton(text="📋 Мои напоминания")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
