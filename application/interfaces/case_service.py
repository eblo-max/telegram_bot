from typing import List, Optional
from dark_archive.domain.entities.case import Case


class CaseService:
    """Интерфейс сервиса для работы с делами"""

    def create_case(self, case: Case) -> Case:
        """Создает новое дело"""
        raise NotImplementedError

    def get_case_by_id(self, case_id: str) -> Optional[Case]:
        """Получает дело по ID"""
        raise NotImplementedError

    def get_cases_by_user_id(self, user_id: int) -> List[Case]:
        """Получает все дела пользователя"""
        raise NotImplementedError

    def update_case(self, case: Case) -> Case:
        """Обновляет дело"""
        raise NotImplementedError

    def delete_case(self, case_id: str) -> bool:
        """Удаляет дело"""
        raise NotImplementedError
