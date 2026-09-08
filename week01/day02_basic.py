import ollama

messages = [
    {
        'role': 'system',
        'content': 'Ты - помощник по программированию.',
    },
    {
        'role': 'user',
        'content': 'Напиши функцию на Python, которая проверяет, является ли число палиндромом',
    },
]

response = ollama.chat(model='qwen2.5:7b', messages=messages)
print(f"Первый ответ: {response.message.content}")

messages.append(response.message)
messages.append(
    {
    'role': 'user',
    'content': 'А теперь добавь к ней обработку отрицательных чисел'
    }
)

response = ollama.chat(model='qwen2.5:7b', messages=messages)
print(f"\nВторой ответ: {response.message.content}")
