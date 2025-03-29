"""Контейнер зависимостей приложения."""

from dependency_injector import containers, providers
from redis import Redis

from dark_archive.infrastructure.services.redis_cache_service import RedisCacheService
from dark_archive.infrastructure.repositories.redis_case_repository import (
    RedisCaseRepository,
)
from dark_archive.domain.services.case_service import CaseService
from dark_archive.presentation.telegram.handlers import TelegramHandlers
from dark_archive.infrastructure.api.telegram.bot_client import TelegramClientAdapter
from dark_archive.infrastructure.api.telegram.telegram_gateway import TelegramGateway
from dark_archive.infrastructure.ai.claude import ClaudeClient
from dark_archive.infrastructure.ai.openai_client import OpenAIClient
from dark_archive.infrastructure.repositories.memory_case_repository import (
    MemoryCaseRepository,
)
from dark_archive.infrastructure.services.lifecycle_monitor import LifecycleMonitor
from dark_archive.config.settings import Settings


class Container(containers.DeclarativeContainer):
    """Контейнер зависимостей приложения."""

    # Конфигурация
    config = providers.Singleton(Settings)

    # Инфраструктурный слой
    redis_client = providers.Singleton(
        Redis,
        host="localhost",
        port=6379,
        db=0,
        decode_responses=True,
    )

    # Репозитории
    memory_case_repository = providers.Singleton(
        MemoryCaseRepository, storage_path="cases"
    )

    redis_case_repository = providers.Singleton(
        RedisCaseRepository, redis_client=redis_client, prefix="case:"
    )

    # Используем Redis репозиторий по умолчанию, если доступен Redis
    case_repository = providers.Singleton(
        lambda redis_repo, memory_repo: memory_repo,
        redis_repo=redis_case_repository,
        memory_repo=memory_case_repository,
    )

    cache_service = providers.Singleton(
        RedisCacheService, redis_client=redis_client, prefix="cache:"
    )

    # AI клиенты
    claude_client = providers.Singleton(
        ClaudeClient,
        api_key="your-api-key",
    )

    openai_client = providers.Singleton(
        OpenAIClient,
        api_key="your-api-key",
    )

    # Выбираем AI клиент на основе конфигурации
    llm_client = providers.Selector(
        "claude",
        claude=claude_client,
        openai=openai_client,
    )

    # Доменный слой
    case_service = providers.Singleton(
        CaseService, case_repository=case_repository, llm_client=llm_client
    )

    # Адаптеры для внешних сервисов
    telegram_client = providers.Singleton(
        TelegramClientAdapter, token="7842890331:AAE6QU3jpYcdUBKl2wBIXRpHj3UR1QFj8-E"
    )

    message_gateway = providers.Singleton(TelegramGateway, client=telegram_client)

    # Презентационный слой
    telegram_handlers = providers.Singleton(
        TelegramHandlers, case_service=case_service, message_gateway=message_gateway
    )

    # Lifecycle monitoring
    lifecycle_monitor = providers.Singleton(
        LifecycleMonitor, check_interval=60  # Check every minute
    )
