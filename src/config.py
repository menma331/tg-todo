import os
from functools import lru_cache

from dotenv import load_dotenv

from utils import singleton

load_dotenv()


@singleton
class Config:
    """Конфиг бота."""

    def __init__(self):
        self.BOT_TOKEN = os.environ.get("BOT_TOKEN")


@lru_cache
def get_config():
    return Config()


settings = Config()
