from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


base_path = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    redis_host: str = Field(alias="REDIS_HOST")
    redis_port: int = Field(alias="REDIS_PORT")
    redis_password: Optional[str] = Field(alias="REDIS_PASSWORD")
    redis_db: int = Field(alias="REDIS_DB", default=0)

    bot_key: str = Field(alias="BOT_KEY")
