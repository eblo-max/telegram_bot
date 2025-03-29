from typing import Dict, List

from dark_archive.domain.entities.achievement import Achievement

# Категории достижений
ACHIEVEMENT_CATEGORIES = {
    "investigation": "Расследование",
    "collection": "Сбор улик",
    "analysis": "Анализ",
    "exploration": "Исследование",
    "cooperation": "Сотрудничество",
}

# Базовые достижения
BASE_ACHIEVEMENTS: List[Dict] = [
    {
        "name": "Начинающий детектив",
        "description": "Завершите первое расследование",
        "category": "investigation",
        "points": 100,
        "requirements": {"completed_cases": 1},
        "rewards": {"experience": 100, "coins": 50},
        "icon": "detective_novice",
    },
    {
        "name": "Собиратель улик",
        "description": "Соберите 10 улик",
        "category": "collection",
        "points": 150,
        "requirements": {"collected_evidence": 10},
        "rewards": {"experience": 150, "coins": 75},
        "icon": "evidence_collector",
    },
    {
        "name": "Аналитик",
        "description": "Проанализируйте 5 улик",
        "category": "analysis",
        "points": 200,
        "requirements": {"analyzed_evidence": 5},
        "rewards": {"experience": 200, "coins": 100},
        "icon": "analyst",
    },
    {
        "name": "Исследователь",
        "description": "Посетите 5 разных локаций",
        "category": "exploration",
        "points": 150,
        "requirements": {"visited_locations": 5},
        "rewards": {"experience": 150, "coins": 75},
        "icon": "explorer",
    },
    {
        "name": "Командный игрок",
        "description": "Участвуйте в 3 совместных расследованиях",
        "category": "cooperation",
        "points": 250,
        "requirements": {"cooperative_cases": 3},
        "rewards": {"experience": 250, "coins": 125},
        "icon": "team_player",
    },
]

# Продвинутые достижения
ADVANCED_ACHIEVEMENTS: List[Dict] = [
    {
        "name": "Опытный детектив",
        "description": "Завершите 10 расследований",
        "category": "investigation",
        "points": 500,
        "requirements": {"completed_cases": 10},
        "rewards": {"experience": 500, "coins": 250},
        "icon": "detective_expert",
    },
    {
        "name": "Мастер улик",
        "description": "Соберите 50 улик",
        "category": "collection",
        "points": 600,
        "requirements": {"collected_evidence": 50},
        "rewards": {"experience": 600, "coins": 300},
        "icon": "evidence_master",
    },
    {
        "name": "Профессиональный аналитик",
        "description": "Проанализируйте 25 улик",
        "category": "analysis",
        "points": 700,
        "requirements": {"analyzed_evidence": 25},
        "rewards": {"experience": 700, "coins": 350},
        "icon": "professional_analyst",
    },
    {
        "name": "Путешественник",
        "description": "Посетите 20 разных локаций",
        "category": "exploration",
        "points": 600,
        "requirements": {"visited_locations": 20},
        "rewards": {"experience": 600, "coins": 300},
        "icon": "traveler",
    },
    {
        "name": "Лидер команды",
        "description": "Участвуйте в 10 совместных расследованиях",
        "category": "cooperation",
        "points": 800,
        "requirements": {"cooperative_cases": 10},
        "rewards": {"experience": 800, "coins": 400},
        "icon": "team_leader",
    },
]

# Секретные достижения
SECRET_ACHIEVEMENTS: List[Dict] = [
    {
        "name": "Скоростной детектив",
        "description": "Завершите расследование менее чем за 24 часа",
        "category": "investigation",
        "points": 1000,
        "requirements": {"case_completion_time": 24},
        "rewards": {"experience": 1000, "coins": 500},
        "icon": "speed_detective",
    },
    {
        "name": "Счастливчик",
        "description": "Найдите редкую улику с первого раза",
        "category": "collection",
        "points": 800,
        "requirements": {"rare_evidence_first_try": 1},
        "rewards": {"experience": 800, "coins": 400},
        "icon": "lucky_finder",
    },
    {
        "name": "Гений анализа",
        "description": "Правильно проанализируйте 10 улик подряд",
        "category": "analysis",
        "points": 1200,
        "requirements": {"consecutive_correct_analysis": 10},
        "rewards": {"experience": 1200, "coins": 600},
        "icon": "analysis_genius",
    },
]


def create_achievements() -> List[Achievement]:
    """Создает все достижения из конфигурации."""
    achievements = []

    for achievement_data in (
        BASE_ACHIEVEMENTS + ADVANCED_ACHIEVEMENTS + SECRET_ACHIEVEMENTS
    ):
        achievement = Achievement.create(**achievement_data)
        achievements.append(achievement)

    return achievements
