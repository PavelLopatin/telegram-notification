# 🕰️ Telegram Reminder Bot

A production-ready **Telegram reminder bot** written in **Python**, allowing users to create **one-time and recurring
reminders** using an interactive button-based interface.

The bot uses **aiogram 3.x**, **APScheduler**, and **Redis** to provide persistent scheduling that survives application
restarts.  
It is fully containerized with **Docker** and **Docker Compose**.

---

## ✨ Features

- 📌 One-time reminders
- 🔁 Recurring reminders:
    - Daily
    - Weekly
    - Monthly
    - Yearly
- 🧠 Persistent scheduler (APScheduler + RedisJobStore)
- 🧩 FSM-based step-by-step forms
- ⌨️ Inline keyboards (no free-text date input required)
- 🔄 Scheduler state survives restarts
- 🐳 Docker & Docker Compose support
- 🌍 Timezone support (default: Europe/Moscow)
- 🚫 No webhooks (long polling only)

---

## 🛠️ Tech Stack

- Python 3.13
- aiogram 3.x
- APScheduler
- Redis
- Docker / Docker Compose

---

## ⚙️ Environment Variables

Environment variables are defined in the **project root**.

### `.env.example`

```env
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=redis
REDIS_DB=0

BOT_KEY=
```

### Setup

1. Create a `.env` file in the project root:

```bash
cp .env.example .env
```

2. Add your Telegram bot token:

```env
BOT_KEY=your_telegram_bot_token_here
```

---

## 🐳 Running with Docker Compose

### Build and start services

```bash
docker compose up -d --build
```

This will start:

- Telegram bot
- Redis (used for storage and scheduling)

### Stop services

```bash
docker compose down
```

---

## 🧠 How It Works

1. User interacts with the bot via inline buttons
2. FSM guides the user through reminder creation
3. Reminder data is stored in Redis
4. APScheduler creates a persistent job in Redis
5. At trigger time, the bot sends a notification
6. Recurring reminders continue until disabled

### Architecture Flow

```
Telegram
  ↓
aiogram (FSM & Handlers)
  ↓
Redis (Reminder Storage)
  ↓
APScheduler (RedisJobStore)
  ↓
Notification
```

---

## ⏰ Scheduler & Persistence

- APScheduler uses RedisJobStore
- Scheduled jobs are stored in Redis
- Jobs are restored automatically after restart
- Reminder business data is stored separately from scheduler jobs

---

## 🔁 Recurring Reminders

Supported repeat modes:

- One-time
- Daily
- Weekly
- Monthly
- Yearly

Recurring reminders are **not deleted after execution** and remain active until disabled by the user.

---

## 🌍 Timezone

- Default timezone: Europe/Moscow
- All reminder times are interpreted in this timezone
- Can be extended to per-user timezones in the future

---

## 🧪 Development Notes

- The bot uses long polling only (no webhooks)
- Webhooks are explicitly removed on startup
- Redis is required for production usage
- Scheduler task functions must be importable (no lambdas or nested functions)

---

## 🐞 Troubleshooting

### Buttons do not appear

- Ensure webhook is deleted on startup
- Verify `BOT_KEY` is set correctly
- Check container logs:

```bash
docker compose logs -f
```

### Reminders disappear after restart

- Redis must be running
- RedisJobStore must be configured
- Do not use MemoryJobStore

---

## 🙌 Author

Built with ❤️ using Python, aiogram, and Redis.
