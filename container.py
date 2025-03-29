import os
from dependency_injector import containers, providers
from telegram.ext import Application
import logging

from dark_archive.application.interfaces.ai_service import IAIService
from dark_archive.application.interfaces.case_repository import ICaseRepository
from dark_archive.application.interfaces.telegram_client import ITelegramClient
from dark_archive.application.use_cases.case_use_cases import (
    CreateCaseUseCase,
    GetCaseUseCase,
    ListCasesUseCase,
)
from dark_archive.application.use_cases.build_theory import BuildTheoryUseCase
from dark_archive.application.use_cases.examine_evidence import (
    ExamineEvidenceUseCase,
)
from dark_archive.application.use_cases.solve_case import SolveCaseUseCase
from dark_archive.application.use_cases.start_investigation import (
    StartInvestigationUseCase,
)
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

    # Репозитории
    case_repository = providers.Singleton(
        MemoryCaseRepository,
    )

    # AI сервис
    claude_service = providers.Singleton(
        ClaudeService,
        api_key=config.anthropic.api_key,
    )

    # Клиент Telegram
    telegram_client = providers.Singleton(
        TelegramClientAdapter,
        token=config.telegram.token,
    )

    telegram_gateway = providers.Singleton(
        TelegramGateway,
        client=telegram_client,
    )

    # Use cases
    create_case_use_case = providers.Singleton(
        CreateCaseUseCase,
        case_repository=case_repository,
        ai_service=claude_service,
    )

    get_case_use_case = providers.Singleton(
        GetCaseUseCase,
        case_repository=case_repository,
    )

    list_cases_use_case = providers.Singleton(
        ListCasesUseCase,
        case_repository=case_repository,
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
