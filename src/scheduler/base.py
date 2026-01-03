from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import settings


jobstores = {
    "default": RedisJobStore(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password,
        db=settings.redis_db,
        jobs_key="apscheduler.jobs",
        run_times_key="apscheduler.run_times"
    )
}

executors = {
    "default": AsyncIOExecutor()
}

job_defaults = {
    "coalesce": False,
    "max_instances": 1
}

scheduler = AsyncIOScheduler(
    jobstores=jobstores,
    executors=executors,
    job_defaults=job_defaults,
    timezone="Europe/Moscow"
)


def start_scheduler():
    scheduler.start()
