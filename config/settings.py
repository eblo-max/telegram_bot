# Created by setup script

import os
from dataclasses import dataclass
from dotenv import load_dotenv
from dark_archive.utils.datetime_utils import get_timezone

# Загружаем переменные окружения из .env файла
load_dotenv()

# Настройки Telegram бота
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Настройки Redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_URL = os.getenv("REDIS_URL", f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")

# Настройки кэширования
CACHE_PREFIX = os.getenv("CACHE_PREFIX", "dark_archive")


@dataclass
class Settings:
    """Класс настроек приложения"""

    # Telegram
    TELEGRAM_TOKEN: str = TELEGRAM_TOKEN

    # Redis
    REDIS_URL: str = REDIS_URL
    REDIS_HOST: str = REDIS_HOST
    REDIS_PORT: int = REDIS_PORT
    REDIS_DB: int = REDIS_DB
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    REDIS_ENABLED: bool = os.getenv("REDIS_ENABLED", "true").lower() == "true"
    REDIS_CASE_PREFIX: str = os.getenv("REDIS_CASE_PREFIX", "case")

    # Storage
    STORAGE_PATH: str = os.getenv("STORAGE_PATH", "data")
    CASES_STORAGE_PATH: str = os.path.join(STORAGE_PATH, "cases.json")

    # AI Providers
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "claude")  # claude или openai

    # Claude AI
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    CLAUDE_MODEL: str = os.getenv("CLAUDE_MODEL", "claude-3-opus-20240229")

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_COMPLETION_MODEL: str = os.getenv(
        "OPENAI_COMPLETION_MODEL", "gpt-4-turbo-preview"
    )
    OPENAI_EMBEDDING_MODEL: str = os.getenv(
        "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
    )

    # Настройки кэширования
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "300"))  # 5 минут по умолчанию
    CACHE_PREFIX: str = CACHE_PREFIX

    # Achievement System Settings
    ACHIEVEMENTS_ENABLED: bool = True
    ACHIEVEMENTS_STORAGE_PATH: str = os.path.join(STORAGE_PATH, "achievements")
    ACHIEVEMENTS_REDIS_PREFIX: str = "achievement"

    def __post_init__(self):
        """Проверяем обязательные настройки"""
        if not self.TELEGRAM_TOKEN:
            raise ValueError("TELEGRAM_TOKEN не установлен")

        if self.AI_PROVIDER == "claude" and not self.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY не установлен")

        if self.AI_PROVIDER == "openai" and not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY не установлен")

        # Создаем директорию для хранения данных
        if not os.path.exists(self.STORAGE_PATH):
            os.makedirs(self.STORAGE_PATH)

        # Create achievements directory if enabled
        if self.ACHIEVEMENTS_ENABLED:
            os.makedirs(self.ACHIEVEMENTS_STORAGE_PATH, exist_ok=True)

    @property
    def timezone(self):
        """Возвращает объект часового пояса"""
        return get_timezone()


# Создаем экземпляр настроек
settings = Settings()
