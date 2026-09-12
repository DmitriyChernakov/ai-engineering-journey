import ollama
import json

from pydantic import BaseModel, field_validator

SYSTEM_PROMPT = """Ты — опытный WEB QA-инженер с 10-летним опытом в автоматизации (Python, Playwright).
Твоя задача: получить описание фичи и сгенерировать тест-кейсы.
Правила работы:
1. Генерируй от 3 до 7 тест-кейсов
2. Включай позитивные, негативные и граничные сценарии
3. Для каждого кейса укажи: название, шаги, ожидаемый результат, приоритет
4. Отвечай строго в JSON
5. Используй только функционал, который указан в описании

Формат:
{
  "test_cases": [
    {
      "id": 1,
      "name": "Краткое название",
      "type": "positive|negative|edge_case",
      "steps": ["шаг 1", "шаг 2"],
      "expected_result": "Что должно произойти",
      "priority": "high|medium|low"
    }
  ]
}"""


class TestCase(BaseModel):
    id: int
    name: str
    type: str
    steps: list[str]
    expected_result: str
    priority: str

    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        allowed = ['positive', 'negative', 'edge_case']
        if v not in allowed:
            raise ValueError(f"Invalid type: {v}. Must be one of {allowed}")
        return v

    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v):
        allowed = ['high', 'medium', 'low']
        if v not in allowed:
            raise ValueError(f"Invalid priority: {v}. Must be one of {allowed}")
        return v


class TestCasesResponse(BaseModel):
    test_cases: list[TestCase]


def generate_test_cases(feature_description: str) -> dict:
    """Генерирует тест-кейсы из описания фичи."""
    response = ollama.chat(
        model='qwen2.5:7b',
        messages=[
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': f'Сгенерируй тест-кейсы для фичи: {feature_description}'}
        ],
        format='json'
    )

    raw_json = response.message.content
    try:
        validated = TestCasesResponse.model_validate_json(raw_json)
        return validated.model_dump()
    except Exception as e:
        print(f"Валидация не удалась: {e}")
        print("Возвращаю сырой JSON без валидации")
        return json.loads(raw_json)


def save_to_file(result: dict, filename: str, feature_name: str) -> None:
    """Сохраняет результат в JSON-файл."""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('{"feature": "' + feature_name + '"}\n')
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Сохранено в {filename}")


if __name__ == '__main__':
    feature = input('Опиши фичу: ')

    print('\nГенерирую тест-кейсы...\n')
    try:
        result = generate_test_cases(feature)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        save_to_file(result, 'test_cases_output.json', feature)
    except Exception as e:
        print(f"Ошибка: {e}")
