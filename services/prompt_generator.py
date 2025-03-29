class PromptGenerator:
    @staticmethod
    def case_generation_prompt() -> str:
        return """
        Сгенерируй мрачное, атмосферное детективное расследование в стиле нуар/хоррор.
        
        Формат ответа должен быть в JSON со следующими полями:
        {
            "title": "Название дела",
            "description": "Подробное описание места преступления и ситуации",
            "evidence": [
                {
                    "id": "уникальный id",
                    "description": "описание улики",
                    "location": "где найдена",
                    "type": "тип улики (вещдок/след/др)",
                    "notes": "заметки детектива"
                }
            ],
            "suspects": [
                {
                    "id": "уникальный id",
                    "name": "имя подозреваемого",
                    "description": "описание внешности и поведения",
                    "alibi": "алиби если есть",
                    "motive": "возможный мотив"
                }
            ],
            "motives": ["список возможных мотивов"],
            "notes": ["важные заметки детектива"]
        }
        
        Стиль: мрачный, жестокий, с элементами хоррора и оккультизма. Используй нецензурную лексику.
        """

    @staticmethod
    def investigation_details_prompt(location: str) -> str:
        return f"""
        Сгенерируй детальное описание осмотра места преступления: {location}
        
        Опиши в стиле нуар/хоррор:
        1. Первое впечатление от места (запахи, звуки, атмосфера)
        2. Детальный осмотр помещения/локации
        3. Найденные улики и их расположение
        4. Следы борьбы или других действий
        5. Необычные детали и аномалии
        6. Заметки детектива и его ощущения
        
        Стиль: максимально мрачный, детальный, с элементами хоррора.
        Используй все органы чувств в описании.
        """

    @staticmethod
    def suspect_profile_prompt(suspect_info: dict) -> str:
        return f"""
        Создай психологический профиль подозреваемого на основе данных:
        Имя: {suspect_info.get('name')}
        Описание: {suspect_info.get('description')}
        Алиби: {suspect_info.get('alibi')}
        Мотив: {suspect_info.get('motive')}
        
        Проанализируй:
        1. Психологический портрет
        2. Вероятность причастности к преступлению
        3. Слабые места и точки давления
        4. Рекомендуемая тактика допроса
        5. Возможные скрытые мотивы
        
        Формат ответа в JSON:
        {{
            "psychological_profile": "подробный анализ",
            "involvement_probability": число от 0 до 1,
            "pressure_points": ["список точек давления"],
            "interrogation_tactics": ["список тактик"],
            "hidden_motives": ["возможные скрытые мотивы"]
        }}
        """

    @staticmethod
    def evidence_analysis_prompt(evidence_list: list, case_context: str) -> str:
        evidence_str = "\n".join([f"- {e}" for e in evidence_list])
        return f"""
        Проанализируй следующие улики в контексте дела:
        
        Контекст дела:
        {case_context}
        
        Улики:
        {evidence_str}
        
        Требуется:
        1. Связи между уликами
        2. Возможные выводы
        3. Противоречия
        4. Что может быть упущено
        5. Приоритетность улик
        
        Формат ответа в JSON:
        {{
            "connections": ["связи между уликами"],
            "conclusions": ["возможные выводы"],
            "contradictions": ["найденные противоречия"],
            "missing_evidence": ["что может быть упущено"],
            "priority_evidence": ["приоритетные улики"]
        }}
        """
