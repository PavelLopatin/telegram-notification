from aiogram.fsm.state import StatesGroup, State


class ReminderForm(StatesGroup):
    text = State()
    repeat_type = State()
    weekday = State()  # weekly
    day = State()  # monthly
    time = State()  # daily / weekly / monthly
    datetime = State()  # once / yearly


class ReminderEditForm(StatesGroup):
    text = State()
