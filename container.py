from dependency_injector import containers, providers
import logging
import os

from dark_archive.infrastructure.api.telegram.bot_client import (
    TelegramClientAdapter,
)
from dark_archive.infrastructure.api.telegram.telegram_gateway import (
    TelegramGateway,
)
from dark_archive.infrastructure.services.claude_service import ClaudeService
from dark_archive.infrastructure.repositories.memory_case_repository import (
    MemoryCaseRepository,
)
from dark_archive.domain.services.case_service import CaseService
from dark_archive.presentation.telegram.handlers import TelegramHandlers


class Container(containers.DeclarativeContainer):
    """Контейнер зависимостей приложения"""

    config = providers.Configuration()

    # Логгер
    logger = providers.Factory(
        logging.getLogger,
        __name__,
    )

    # Инфраструктурный слой
    telegram_client = providers.Singleton(
        TelegramClientAdapter,
        token=os.environ["TELEGRAM_TOKEN"],
    )

    telegram_gateway = providers.Singleton(
        TelegramGateway,
        client=telegram_client,
    )

    claude_service = providers.Singleton(
        ClaudeService,
        api_key=os.environ["ANTHROPIC_API_KEY"],
    )

    case_repository = providers.Singleton(
        MemoryCaseRepository,
    )

    # Доменный слой
    case_service = providers.Singleton(
        CaseService,
        case_repository=case_repository,
        ai_service=claude_service,
    )

    # Презентационный слой
    telegram_handlers = providers.Singleton(
        TelegramHandlers,
        telegram_client=telegram_client,
        case_service=case_service,
        message_gateway=telegram_gateway,
    )
