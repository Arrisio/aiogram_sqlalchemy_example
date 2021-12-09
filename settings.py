import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "postgres"

    TG_BOT_TOKEN: str
    TG_BOT_ADMIN_ID: str

    SENTRY_URL: str = ""

    LOGURU_FORMAT = "<level>{level: <8} {time:YYYY-MM-DD HH:mm:ss}</level>|<cyan>{name:<12}</cyan>:<cyan>{function:<24}</cyan>:<cyan>{line}</cyan> - <level>{message:>32}</level>|{extra}"
    class Config:
        env_file: str = ".env" if os.path.exists(".env") else "../.env"
        env_file_encoding = "utf-8"

settings = Settings()