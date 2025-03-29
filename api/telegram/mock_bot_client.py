from typing import List, Optional
from dataclasses import dataclass, field

from dark_archive.application.interfaces.message_gateway import IMessageGateway
from dark_archive.domain.value_objects.message import OutboundMessage, Button


@dataclass
class MockTelegramClient(IMessageGateway):
    """Мок клиент Telegram для тестирования."""

    sent_messages: List[OutboundMessage] = field(default_factory=list)

    async def initialize(self) -> bool:
        """Инициализирует клиент."""
        return True

    async def shutdown(self) -> bool:
        """Завершает работу клиента."""
        return True

    def is_healthy(self) -> bool:
        """Проверяет здоровье клиента."""
        return True

    async def send_message(
        self,
        chat_id: int,
        text: str,
        buttons: Optional[List[Button]] = None,
        image_path: Optional[str] = None,
    ) -> bool:
        """Отправляет сообщение."""
        message = OutboundMessage(
            chat_id=chat_id, text=text, buttons=buttons or [], image_path=image_path
        )
        self.sent_messages.append(message)
        return True

    async def get_sent_messages(self) -> List[OutboundMessage]:
        """Возвращает отправленные сообщения."""
        return self.sent_messages
