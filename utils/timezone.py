import pytz
from datetime import datetime


def get_current_time():
    """Возвращает текущее время в UTC"""
    return datetime.now(pytz.UTC)


def get_timezone():
    """Возвращает UTC"""
    return pytz.UTC
