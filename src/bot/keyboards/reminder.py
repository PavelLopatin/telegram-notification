def reminder_actions(reminder_id: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✏️ Редактировать",
                    callback_data=f"reminder:edit:{reminder_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Удалить",
                    callback_data=f"reminder:delete:{reminder_id}"
                ),
            ]
        ]
    )


from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def edit_menu(reminder_id: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📝 Текст",
                    callback_data=f"reminder:edit:text:{reminder_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data="reminder:edit:cancel"
                )
            ],
        ]
    )
