from typing import Dict, Optional, List
from .client import ClaudeClient


class MockClaudeClient(ClaudeClient):
    """Мок-клиент для тестирования"""

    def __init__(self):
        super().__init__(api_key="test_key")
        self._responses: List[Dict[str, str]] = []
        self._messages: List[Dict[str, str]] = []

    async def generate_text(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        context: Optional[Dict[str, str]] = None,
    ) -> Optional[str]:
        """Генерирует тестовый текст"""
        self._messages.append({"role": "user", "content": prompt})

        if self._responses:
            response = self._responses.pop(0)
            self._messages.append({"role": "assistant", "content": response["content"]})
            return response["content"]

        return "Test response"

    async def analyze_text(
        self, text: str, instruction: str, context: Optional[Dict[str, str]] = None
    ) -> Optional[Dict]:
        """Анализирует текст"""
        return {"analysis": "Test analysis", "confidence": 0.8}

    def add_response(self, content: str):
        """Добавляет тестовый ответ"""
        self._responses.append({"content": content})

    def get_messages(self) -> List[Dict[str, str]]:
        """Возвращает все сообщения"""
        return self._messages

    def clear(self):
        """Очищает историю сообщений и ответов"""
        self._messages.clear()
        self._responses.clear()
