from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Button:
    """Кнопка для клавиатуры Telegram"""

    text: str
    callback_data: str


@dataclass
class Message:
    """Сообщение для отправки в Telegram"""

    text: str
    parse_mode: Optional[str] = None
    keyboard_buttons: Optional[List[List[Button]]] = None
