from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def time_picker_keyboard(
    start_hour: int = 9,
    end_hour: int = 20,
):
    buttons = []

    for hour in range(start_hour, end_hour + 1):
        time_str = f"{hour:02d}:00"
        buttons.append(
            InlineKeyboardButton(
                text=time_str,
                callback_data=f"time:{time_str}"
            )
        )

    # разбиваем по 3 кнопки в строке
    keyboard = [
        buttons[i:i + 3]
        for i in range(0, len(buttons), 3)
    ]

    # fallback
    keyboard.append([
        InlineKeyboardButton(
            text="✍️ Ввести вручную",
            callback_data="time:manual"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
