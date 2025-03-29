"""Клиент для взаимодействия с OpenAI API."""

import json
import logging
from typing import Dict, Optional
import openai

from dark_archive.domain.interfaces.llm_client import ILLMClient

logger = logging.getLogger(__name__)


class OpenAIClient(ILLMClient):
    """Клиент для взаимодействия с OpenAI API."""

    def __init__(self, api_key: str):
        self._api_key = api_key
        self._client = None
        self._initialized = False
        self._logger = logging.getLogger(__name__)
        self._completion_model = "gpt-4-turbo-preview"
        self._embedding_model = "text-embedding-3-small"

    async def initialize(self) -> bool:
        """Инициализирует клиент."""
        try:
            import openai

            openai.api_key = self._api_key
            self._client = openai
            self._initialized = True
            self._logger.info("OpenAI client initialized successfully")
            return True
        except Exception as e:
            self._logger.error(f"Failed to initialize OpenAI client: {e}")
            return False

    async def shutdown(self) -> None:
        """Завершает работу клиента."""
        try:
            self._client = None
            self._initialized = False
            self._logger.info("OpenAI client shut down successfully")
        except Exception as e:
            self._logger.error(f"Error shutting down OpenAI client: {e}")

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
            self._logger.error(f"Failed to recover OpenAI client: {e}")
            return False

    async def generate_text(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        context: Optional[Dict[str, str]] = None,
    ) -> Optional[str]:
        """Генерирует текст с помощью OpenAI"""
        try:
            if context:
                context_str = "\n".join(f"{k}: {v}" for k, v in context.items())
                prompt = f"Context:\n{context_str}\n\nPrompt:\n{prompt}"

            response = await self._client.chat.completions.create(
                model=self._completion_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )

            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating text with OpenAI: {str(e)}")
            return None

    async def analyze_text(
        self, text: str, instruction: str, context: Optional[Dict[str, str]] = None
    ) -> Optional[Dict]:
        """Анализирует текст с помощью OpenAI"""
        try:
            context_str = ""
            if context:
                context_str = f"\nAdditional context:\n{json.dumps(context, indent=2)}"

            prompt = f"Instruction: {instruction}\n\nText to analyze:\n{text}{context_str}\n\nPlease provide the analysis in valid JSON format."

            response = await self._client.chat.completions.create(
                model=self._completion_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )

            result = response.choices[0].message.content
            return json.loads(result)
        except Exception as e:
            logger.error(f"Error analyzing text with OpenAI: {str(e)}")
            return None

    async def get_embedding(self, text: str) -> Optional[list[float]]:
        """Получает эмбеддинг текста с помощью OpenAI"""
        try:
            response = await self._client.embeddings.create(
                model=self._embedding_model, input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error getting embedding from OpenAI: {str(e)}")
            return None
