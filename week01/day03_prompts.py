import ollama

MODEL = "qwen2.5:7b"
REVIEW = "Доставка быстрая, но упаковка помята. Сам товар работает отлично."


def run_prompt(name: str, prompt: str):
    print(f"\n{'=' * 60}")
    print(f"Техника: {name}")
    print('=' * 60)
    response = ollama.chat(
        model=MODEL,
        messages=[{'role': 'user', 'content': prompt}]
    )
    print(response.message.content)
    print()


# === 1. ZERO-SHOT ===
prompt_zero_shot = f"""
Определи тональность отзыва: положительный, отрицательный или смешанный.

Отзыв: {REVIEW}
Ответ:
"""

# === 2. FEW-SHOT ===
prompt_few_shot = f"""
Определи тональность отзыва. Дай ответ по примеру

Примеры:

Отзыв: "Всё отлично, рекомендую!"
Тональность: Положительный

Отзыв: "Ужасный сервис, больше не приду"
Тональность: Отрицательный

Отзыв: "Обычный товар, ничего особенного"
Тональность: Нейтральный


Классифицируй этот отзыв:
Отзыв: "{REVIEW}"
Тональность:
"""

# === 3. CHAIN-OF-THOUGHT ===
prompt_cot = f"""
Проанализируй отзыв шаг за шагом.
Сначала выдели плюсы, потом минусы, потом сделай вывод о тональности.

Отзыв: {REVIEW}

Анализ:
"""

# === 4. STRUCTURED OUTPUT ===
prompt_structured = f"""
Проанализируй отзыв и верни результат СТРОГО в JSON:
{'''{
  "sentiment": "positive|negative|mixed",
  "pros": [...],
  "cons": [...],
  "confidence": 0.0-1.0
}'''
}

Отзыв: {REVIEW}
JSON:
"""

if __name__ == '__main__':
    run_prompt("Zero-shot", prompt_zero_shot)
    run_prompt("Few-shot", prompt_few_shot)
    run_prompt("Chain-of-Thought", prompt_cot)
    run_prompt("Structured Output", prompt_structured)
