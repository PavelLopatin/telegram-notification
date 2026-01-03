import uuid
from calendar import monthrange
from datetime import datetime, timedelta

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message
from apscheduler.jobstores.base import JobLookupError

from scheduler.base import scheduler
from scheduler.tasks import send_reminder
from storage import redis_client
from ..keyboards.menu import main_menu
from ..keyboards.reminder import reminder_actions, edit_menu
from ..keyboards.repeat import repeat_type_keyboard, weekday_keyboard, monthday_keyboard
from ..keyboards.timepicker import time_picker_keyboard
from ..states.reminder import ReminderForm, ReminderEditForm


router = Router()

TYPE_MAP = {
    "once": "Один раз",
    "daily": "Каждый день",
    "weekly": "Каждую неделю",
    "monthly": "Каждый месяц",
    "yearly": "Каждый год",
}


async def create_reminder(
    *,
    user_id: int,
    text: str,
    run_at: datetime,
    repeat_type: str,
):
    reminder_id = str(uuid.uuid4())
    job_id = f"reminder_{reminder_id}"

    # 1️⃣ сохраняем в Redis
    await redis_client.hset(
        f"reminder:{reminder_id}",
        mapping={
            "user_id": user_id,
            "text": text,
            "run_at": run_at.isoformat(),
            "type": repeat_type,
            "status": "active",
        }
    )
    await redis_client.sadd(f"user:{user_id}:reminders", reminder_id)

    # 2️⃣ создаём job
    if repeat_type == "once":
        scheduler.add_job(
            send_reminder,
            "date",
            run_date=run_at,
            args=(reminder_id,),
            id=job_id,
            replace_existing=True,
        )

    elif repeat_type == "daily":
        scheduler.add_job(
            send_reminder,
            "interval",
            days=1,
            start_date=run_at,
            args=(reminder_id,),
            id=job_id,
            replace_existing=True,
        )

    elif repeat_type == "weekly":
        scheduler.add_job(
            send_reminder,
            "cron",
            day_of_week=run_at.weekday(),
            hour=run_at.hour,
            minute=run_at.minute,
            args=(reminder_id,),
            id=job_id,
            replace_existing=True,
        )

    elif repeat_type == "monthly":
        scheduler.add_job(
            send_reminder,
            "cron",
            day=run_at.day,
            hour=run_at.hour,
            minute=run_at.minute,
            args=(reminder_id,),
            id=job_id,
            replace_existing=True,
        )

    elif repeat_type == "yearly":
        scheduler.add_job(
            send_reminder,
            "cron",
            month=run_at.month,
            day=run_at.day,
            hour=run_at.hour,
            minute=run_at.minute,
            args=(reminder_id,),
            id=job_id,
            replace_existing=True,
        )

    else:
        raise ValueError(f"Unknown repeat_type: {repeat_type}")

    return reminder_id


@router.message(F.text == "/start")
async def start(message: Message):
    await message.answer(
        "Привет! Я бот-напоминалка ⏰",
        reply_markup=main_menu()
    )


@router.message(F.text == "➕ Добавить напоминание")
async def add_reminder(message: Message, state: FSMContext):
    await message.answer("📝 Что нужно напомнить?")
    await state.set_state(ReminderForm.text)


@router.message(ReminderForm.text)
async def reminder_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text)

    await message.answer(
        "🔁 Как часто повторять напоминание?",
        reply_markup=repeat_type_keyboard()
    )
    await state.set_state(ReminderForm.repeat_type)


@router.callback_query(ReminderForm.repeat_type, F.data.startswith("repeat:"))
async def pick_repeat_type(callback: CallbackQuery, state: FSMContext):
    repeat_type = callback.data.split(":")[1]
    await state.update_data(repeat_type=repeat_type)

    if repeat_type == "daily":
        await callback.message.edit_text(
            "⏰ Во сколько напоминать?",
            reply_markup=time_picker_keyboard()
        )
        await state.set_state(ReminderForm.time)

    elif repeat_type == "weekly":
        await callback.message.edit_text(
            "📅 В какой день недели?",
            reply_markup=weekday_keyboard()
        )
        await state.set_state(ReminderForm.weekday)

    elif repeat_type == "monthly":
        await callback.message.edit_text(
            "📅 Какого числа месяца?",
            reply_markup=monthday_keyboard()
        )
        await state.set_state(ReminderForm.day)

    else:  # once / yearly
        await callback.message.edit_text(
            "📅 Когда напомнить?\nDD.MM.YYYY HH:MM"
        )
        await state.set_state(ReminderForm.datetime)

    await callback.answer()


@router.callback_query(ReminderForm.weekday, F.data.startswith("wd:"))
async def pick_weekday(callback: CallbackQuery, state: FSMContext):
    weekday = int(callback.data.split(":")[1])
    await state.update_data(weekday=weekday)

    await callback.message.edit_text(
        "⏰ Во сколько напоминать?",
        reply_markup=time_picker_keyboard()
    )
    await state.set_state(ReminderForm.time)
    await callback.answer()


@router.callback_query(ReminderForm.day, F.data.startswith("md:"))
async def pick_monthday(callback: CallbackQuery, state: FSMContext):
    value = callback.data.split(":")[1]

    if value == "last":
        await state.update_data(day="last")
    else:
        await state.update_data(day=int(value))

    await callback.message.edit_text(
        "⏰ Во сколько напоминать?",
        reply_markup=time_picker_keyboard()
    )
    await state.set_state(ReminderForm.time)
    await callback.answer()


async def handle_time_selected(
    *,
    hour: int,
    minute: int,
    user_id: int,
    state,
    send_answer,
):
    data = await state.get_data()
    repeat_type = data["repeat_type"]
    text = data["text"]
    now = datetime.now()

    if repeat_type == "daily":
        run_at = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if run_at <= now:
            run_at += timedelta(days=1)

    elif repeat_type == "weekly":
        weekday = data["weekday"]
        run_at = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        days_ahead = (weekday - run_at.weekday()) % 7
        if days_ahead == 0 and run_at <= now:
            days_ahead = 7
        run_at += timedelta(days=days_ahead)

    elif repeat_type == "monthly":
        day = data["day"]
        year, month = now.year, now.month

        if day == "last":
            day = monthrange(year, month)[1]

        run_at = now.replace(hour=hour, minute=minute, second=0, microsecond=0, day=day)

        if run_at <= now:
            month += 1
            if month == 13:
                month = 1
                year += 1

            if data["day"] == "last":
                day = monthrange(year, month)[1]

            run_at = run_at.replace(year=year, month=month, day=day)

    else:
        raise ValueError("Unsupported repeat_type for time picker")

    await create_reminder(
        user_id=user_id,
        text=text,
        run_at=run_at,
        repeat_type=repeat_type,
    )

    await send_answer("✅ Напоминание сохранено!")
    await state.clear()


@router.callback_query(ReminderForm.time, F.data.startswith("time:"))
async def pick_time_inline(callback: CallbackQuery, state: FSMContext):
    values = callback.data.split(":")

    if values[1] == "manual":
        await callback.message.edit_text("⏰ Введи время вручную\nHH:MM")
        await callback.answer()
        return

    hour, minute = map(int, values[1:])

    await handle_time_selected(
        hour=hour,
        minute=minute,
        user_id=callback.from_user.id,
        state=state,
        send_answer=callback.message.answer,
    )

    await callback.answer()


@router.message(ReminderForm.datetime)
async def reminder_datetime(message: Message, state: FSMContext):
    data = await state.get_data()
    repeat_type = data["repeat_type"]

    try:
        run_at = datetime.strptime(message.text, "%d.%m.%Y %H:%M")
    except ValueError:
        await message.answer("❌ Неверный формат.")
        return

    await create_reminder(
        user_id=message.from_user.id,
        text=data["text"],
        run_at=run_at,
        repeat_type=repeat_type,
    )

    await message.answer("✅ Напоминание сохранено!")
    await state.clear()


@router.message(ReminderForm.time)
async def pick_time_text(message: Message, state: FSMContext):
    try:
        hour, minute = map(int, message.text.split(":"))
        assert 0 <= hour < 24 and 0 <= minute < 60
    except Exception:
        await message.answer("❌ Формат времени: HH:MM")
        return

    await handle_time_selected(
        hour=hour,
        minute=minute,
        user_id=message.from_user.id,
        state=state,
        send_answer=message.answer,
    )


@router.message(F.text == "📋 Мои напоминания")
async def list_reminders(message: Message):
    user_id = message.from_user.id
    reminder_ids = await redis_client.smembers(f"user:{user_id}:reminders")

    if not reminder_ids:
        await message.answer("У тебя пока нет напоминаний 🙃")
        return

    for rid in reminder_ids:
        data = await redis_client.hgetall(f"reminder:{rid}")

        if not data:
            continue

        run_at = datetime.fromisoformat(data["run_at"]).strftime("%d.%m.%Y %H:%M")
        repeat = TYPE_MAP.get(data["type"], data["type"])
        text = (
            f"⏰ {run_at}\n"
            f"📝 {data['text']}\n"
            f"🔁 {repeat}"
        )

        await message.answer(
            text,
            reply_markup=reminder_actions(rid)
        )


@router.callback_query(F.data.startswith("reminder:delete:"))
async def delete_reminder(callback: CallbackQuery):
    _, action, reminder_id = callback.data.split(":")

    key = f"reminder:{reminder_id}"
    data = await redis_client.hgetall(key)

    if not data:
        await callback.answer("Напоминание уже удалено", show_alert=True)
        return

    user_id = int(data["user_id"])

    try:
        scheduler.remove_job(f"reminder_{reminder_id}")
    except JobLookupError:
        pass

    await redis_client.delete(key)
    await redis_client.srem(f"user:{user_id}:reminders", reminder_id)

    await callback.message.edit_text("❌ Напоминание удалено")
    await callback.answer()


@router.callback_query(F.data == "reminder:edit:cancel")
async def cancel_edit(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Редактирование отменено")
    await callback.answer()


@router.callback_query(F.data.regexp(r"^reminder:edit:[^:]+$"))
async def edit_reminder_menu(callback: CallbackQuery, state: FSMContext):
    reminder_id = callback.data.split(":")[-1]

    data = await redis_client.hgetall(f"reminder:{reminder_id}")
    if not data:
        await callback.answer("Напоминание не найдено", show_alert=True)
        return

    await state.update_data(reminder_id=reminder_id)

    await callback.message.answer(
        "✏️ Что ты хочешь изменить?",
        reply_markup=edit_menu(reminder_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("reminder:edit:text:"))
async def edit_text_start(callback: CallbackQuery, state: FSMContext):
    reminder_id = callback.data.split(":")[-1]

    reminder = await redis_client.hgetall(f"reminder:{reminder_id}")
    if not reminder:
        await callback.answer("Напоминание не найдено", show_alert=True)
        return

    # сохраняем reminder_id в FSM
    await state.update_data(reminder_id=reminder_id)

    # ВАЖНО: именно answer, а не edit_text
    await callback.message.answer(
        f"📝 Текущий текст:\n\n{reminder['text']}\n\n"
        f"✏️ Введи новый текст напоминания:"
    )

    await state.set_state(ReminderEditForm.text)
    await callback.answer()


@router.message(ReminderEditForm.text)
async def save_edited_text(message: Message, state: FSMContext):
    data = await state.get_data()
    reminder_id = data.get("reminder_id")

    if not reminder_id:
        await message.answer("❌ Ошибка состояния. Попробуй снова.")
        await state.clear()
        return

    reminder = await redis_client.hgetall(f"reminder:{reminder_id}")
    if not reminder:
        await message.answer("❌ Напоминание не найдено.")
        await state.clear()
        return

    old_text = reminder.get("text")

    if message.text == old_text:
        await message.answer("ℹ️ Текст не изменился")
        await state.clear()
        return

    await redis_client.hset(
        f"reminder:{reminder_id}",
        "text",
        message.text
    )

    await message.answer("✅ Текст напоминания обновлён")
    await state.clear()
