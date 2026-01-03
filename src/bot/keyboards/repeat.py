from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def repeat_type_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Один раз", callback_data="repeat:once")],
            [InlineKeyboardButton(text="Каждый день", callback_data="repeat:daily")],
            [InlineKeyboardButton(text="Каждую неделю", callback_data="repeat:weekly")],
            [InlineKeyboardButton(text="Каждый месяц", callback_data="repeat:monthly")],
            [InlineKeyboardButton(text="Каждый год", callback_data="repeat:yearly")],
        ]
    )


def weekday_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Пн", callback_data="wd:0"),
                InlineKeyboardButton(text="Вт", callback_data="wd:1"),
                InlineKeyboardButton(text="Ср", callback_data="wd:2"),
                InlineKeyboardButton(text="Чт", callback_data="wd:3"),
                InlineKeyboardButton(text="Пт", callback_data="wd:4"),
                InlineKeyboardButton(text="Сб", callback_data="wd:5"),
                InlineKeyboardButton(text="Вс", callback_data="wd:6"),
            ]
        ]
    )


def monthday_keyboard():
    buttons = [
        InlineKeyboardButton(text=str(i), callback_data=f"md:{i}")
        for i in range(1, 29)
    ]

    keyboard = [
        buttons[i:i + 7]
        for i in range(0, len(buttons), 7)
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
