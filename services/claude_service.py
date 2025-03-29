from anthropic import Anthropic
from typing import Dict, Optional, List
from dark_archive.domain.interfaces.ai_service import IAIService
from dark_archive.domain.services.prompt_generator import PromptGenerator
import json
import uuid


class ClaudeService(IAIService):
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        self.prompt_generator = PromptGenerator()

    def _generate_response(
        self, prompt: str, max_tokens: int = 1000, temperature: float = 0.9
    ) -> Optional[str]:
        try:
            response = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text
        except Exception as e:
            print(f"Ошибка генерации ответа: {e}")
            return None

    def generate_case(self) -> Optional[Dict]:
        prompt = self.prompt_generator.case_generation_prompt()
        response = self._generate_response(prompt, max_tokens=1500)

        if not response:
            return None

        try:
            case_data = json.loads(response)
            # Добавляем уникальные ID для улик и подозреваемых если их нет
            for evidence in case_data.get("evidence", []):
                if "id" not in evidence:
                    evidence["id"] = str(uuid.uuid4())
            for suspect in case_data.get("suspects", []):
                if "id" not in suspect:
                    suspect["id"] = str(uuid.uuid4())
            return case_data
        except json.JSONDecodeError as e:
            print(f"Ошибка парсинга JSON: {e}")
            return None

    def generate_investigation_details(self, location: str) -> Optional[str]:
        prompt = self.prompt_generator.investigation_details_prompt(location)
        return self._generate_response(prompt, max_tokens=800, temperature=0.85)

    def generate_interrogation(self, suspect: str, case_details: str) -> Optional[str]:
        prompt = f"""
        Сгенерируй диалог допроса подозреваемого: {suspect}
        
        Контекст дела: {case_details}
        
        Стиль допроса:
        1. Жесткий, давящий
        2. С элементами психологического давления
        3. Используй нецензурную лексику
        4. Подозреваемый должен сопротивляться и юлить
        """
        return self._generate_response(prompt, max_tokens=1000, temperature=0.9)

    def analyze_evidence(
        self, evidence_list: List[str], case_context: str
    ) -> Optional[Dict]:
        prompt = self.prompt_generator.evidence_analysis_prompt(
            evidence_list, case_context
        )
        response = self._generate_response(prompt, max_tokens=1000)

        if not response:
            return None

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return None

    def generate_suspect_profile(self, suspect_info: Dict) -> Optional[Dict]:
        prompt = self.prompt_generator.suspect_profile_prompt(suspect_info)
        response = self._generate_response(prompt, max_tokens=800)

        if not response:
            return None

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return None

    def generate_case_summary(self, case_data: Dict) -> Optional[str]:
        prompt = f"""
        Создай краткую сводку по делу на основе следующих данных:
        {json.dumps(case_data, ensure_ascii=False, indent=2)}
        
        Формат:
        1. Основные факты
        2. Ключевые улики
        3. Главные подозреваемые
        4. Текущие гипотезы
        5. Следующие шаги
        
        Стиль: краткий, информативный, в стиле полицейского отчета
        """
        return self._generate_response(prompt, max_tokens=500, temperature=0.7)

    def generate_next_steps(
        self, case_data: Dict, current_progress: Dict
    ) -> Optional[List[str]]:
        prompt = f"""
        На основе данных дела и текущего прогресса предложи следующие шаги расследования.
        
        Данные дела:
        {json.dumps(case_data, ensure_ascii=False, indent=2)}
        
        Текущий прогресс:
        {json.dumps(current_progress, ensure_ascii=False, indent=2)}
        
        Требуется список конкретных действий в порядке приоритета.
        Каждое действие должно быть конкретным и выполнимым.
        
        Формат ответа в JSON:
        {{"next_steps": ["список действий"]}}
        """

        response = self._generate_response(prompt, max_tokens=500, temperature=0.7)
        if not response:
            return None

        try:
            data = json.loads(response)
            return data.get("next_steps", [])
        except json.JSONDecodeError:
            return None
