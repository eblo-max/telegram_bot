from datetime import datetime
import pytz

# Создаем объект часового пояса один раз
TIMEZONE = pytz.timezone("Europe/Moscow")


def get_current_time() -> datetime:
    """Возвращает текущее время в московском часовом поясе"""
    return datetime.now(TIMEZONE)


def get_timezone():
    """Возвращает объект часового пояса pytz"""
    return TIMEZONE


def localize_datetime(dt: datetime) -> datetime:
    """Локализует datetime объект в московский часовой пояс"""
    if dt.tzinfo is None:
        return TIMEZONE.localize(dt)
    return dt.astimezone(TIMEZONE)
