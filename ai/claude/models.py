from dataclasses import dataclass
from typing import Dict, Optional, List


@dataclass
class ClaudeMessage:
    """Модель сообщения для Claude API"""

    role: str
    content: str


@dataclass
class ClaudeResponse:
    """Модель ответа от Claude API"""

    content: List[Dict[str, str]]
    model: str
    usage: Dict[str, int]


@dataclass
class ClaudeCompletion:
    """Модель завершения для старого Completion API"""

    completion: str
    model: str
    usage: Dict[str, int]


@dataclass
class ClaudeConfig:
    """Конфигурация для Claude API"""

    api_key: str
    model: str = "claude-3-opus-20240229"
    max_tokens: int = 1000
    temperature: float = 0.7
    response_format: Optional[Dict[str, str]] = None
