import json
import logging
from typing import Dict, Optional, Any
import anthropic

from dark_archive.domain.interfaces.llm_client import ILLMClient

logger = logging.getLogger(__name__)


class ClaudeClient(ILLMClient):
    """Клиент для взаимодействия с Claude API."""

    def __init__(self, api_key: str):
        self._api_key = api_key
        self._client = None
        self._initialized = False
        self._logger = logging.getLogger(__name__)
        self._model = "claude-3-opus-20240229"
        self._api_version = anthropic.__version__

    async def initialize(self) -> bool:
        """Инициализирует клиент."""
        try:
            from anthropic import AsyncAnthropic

            self._client = AsyncAnthropic(api_key=self._api_key)
            self._initialized = True
            self._logger.info("Claude client initialized successfully")
            return True
        except Exception as e:
            self._logger.error(f"Failed to initialize Claude client: {e}")
            return False

    async def shutdown(self) -> None:
        """Завершает работу клиента."""
        try:
            self._client = None
            self._initialized = False
            self._logger.info("Claude client shut down successfully")
        except Exception as e:
            self._logger.error(f"Error shutting down Claude client: {e}")

    async def health_check(self) -> bool:
        """Проверяет состояние клиента."""
        return self._initialized and self._client is not None

    async def recover(self) -> bool:
        """Восстанавливает работу клиента после сбоя."""
        try:
            if not self._initialized:
                return await self.initialize()
            return True
        except Exception as e:
            self._logger.error(f"Failed to recover Claude client: {e}")
            return False

    def _is_messages_api(self) -> bool:
        """Проверяет, доступен ли Messages API"""
        return hasattr(self._client, "messages")

    async def generate_text(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        context: Optional[Dict[str, str]] = None,
    ) -> Optional[str]:
        """Генерирует текст с помощью Claude"""
        try:
            # Добавляем контекст к промпту если он есть
            if context:
                context_str = "\n".join(f"{k}: {v}" for k, v in context.items())
                prompt = f"Context:\n{context_str}\n\nPrompt:\n{prompt}"

            if self._is_messages_api():
                response = await self._client.messages.create(
                    model=self._model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[{"role": "user", "content": prompt}],
                )
                return response.content[0].text
            else:
                return await self._generate_with_completion(
                    prompt, max_tokens, temperature
                )

        except Exception as e:
            logger.error(f"Error generating text with Claude: {str(e)}")
            return None

    async def analyze_text(
        self, text: str, instruction: str, context: Optional[Dict[str, str]] = None
    ) -> Optional[Dict]:
        """Анализирует текст с помощью Claude"""
        try:
            context_str = (
                f"Additional context:\n{json.dumps(context, indent=2)}"
                if context
                else ""
            )
            prompt = f"""
            {instruction}

            Text to analyze:
            {text}

            {context_str}

            Please provide the analysis in valid JSON format.
            """

            response = await self._client.messages.create(
                model=self._model,
                temperature=0.2,  # Низкая температура для более точного анализа
                messages=[{"role": "user", "content": prompt}],
            )

            # Извлекаем JSON из ответа
            try:
                return json.loads(response.content[0].text)
            except json.JSONDecodeError:
                logger.error("Failed to parse JSON from Claude response")
                return None

        except Exception as e:
            logger.error(f"Error analyzing text with Claude: {str(e)}")
            return None

    async def get_embedding(self, text: str) -> Optional[list[float]]:
        """
        Получает эмбеддинги с помощью Claude.
        Note: В текущей версии Claude API не поддерживает прямое получение эмбеддингов.
        Этот метод следует реализовать с использованием других моделей или сервисов.
        """
        logger.warning("Embedding generation is not supported by Claude API")
        return None

    async def _generate_with_completion(
        self, prompt: str, max_tokens: int, temperature: float
    ) -> str:
        """Использует старый Completion API"""
        try:
            from anthropic import HUMAN_PROMPT, AI_PROMPT

            formatted_prompt = f"{HUMAN_PROMPT} {prompt} {AI_PROMPT}"
        except ImportError:
            # Fallback для совсем старых версий
            formatted_prompt = f"\n\nHuman: {prompt}\n\nAssistant:"

        response = await self._client.completions.create(
            prompt=formatted_prompt,
            model=self._model,
            max_tokens_to_sample=max_tokens,
            temperature=temperature,
        )
        return response.completion
