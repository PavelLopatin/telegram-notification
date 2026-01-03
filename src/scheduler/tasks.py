from bot import bot
from storage import redis_client


async def send_reminder(reminder_id: str):
    data = await redis_client.hgetall(f"reminder:{reminder_id}")

    if not data or data.get("status") != "active":
        return

    user_id = int(data["user_id"])
    text = data["text"]
    repeat_type = data["type"]

    await bot.send_message(
        user_id,
        f"⏰ Напоминание:\n{text}"
    )

    # 🧹 если одноразовое — удаляем
    if repeat_type == "once":
        await redis_client.delete(f"reminder:{reminder_id}")
        await redis_client.srem(f"user:{user_id}:reminders", reminder_id)
