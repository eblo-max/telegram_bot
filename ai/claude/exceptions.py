class ClaudeAPIError(Exception):
    """Базовое исключение для ошибок Claude API"""

    pass


class ClaudeAuthenticationError(ClaudeAPIError):
    """Ошибка аутентификации в Claude API"""

    pass


class ClaudeRateLimitError(ClaudeAPIError):
    """Ошибка превышения лимита запросов к Claude API"""

    pass


class ClaudeModelNotFoundError(ClaudeAPIError):
    """Ошибка: модель не найдена"""

    pass


class ClaudeInvalidRequestError(ClaudeAPIError):
    """Ошибка: неверный запрос к Claude API"""

    pass


class ClaudeResponseError(ClaudeAPIError):
    """Ошибка при обработке ответа от Claude API"""

    pass
