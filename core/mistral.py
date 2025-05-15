# 1. poetry add mistralai
# 2. определить API ключ

API_KEY = r"D1ue61Z6eyKipepIK7dweOdrXjpxLle5"
from mistralai import Mistral
from pprint import pprint
# 3. Тестовый код для проверки работы модерации


client = Mistral(api_key=API_KEY)

response = client.classifiers.moderate_chat(
    model="mistral-moderation-latest",
    inputs=[
        {"role": "user", "content": "Джойказино азино три топора. Лучшее онлайн казино в СНГ. Фриспины за ваши почки!!!!!!!!!"},
    ],
)

raw_result = response.results[0].category_scores
result = {key: round(value, 2) for key, value in raw_result.items()}
pprint(result)


# 4. Словарик грейдов для оценки отзывов

MISTRAL_MODERATIONS_GRADES = {
        'hate_and_discrimination': 0.2, # ненависть и дискриминация
        'sexual': 0.2, # сексуальный
        'violence_and_threats': 0.2, # насилие и угрозы
        'dangerous_and_criminal_content': 0.2, # опасный и криминальный контент
        'selfharm': 0.2, # самоповреждение
        'health': 0.2, # здоровье
        'financial': 0.2, # финансовый
        'law': 0.2, # закон
        'pii': 0.2, # личная информация
}


# 5. Функция для оценки отзыва:

def moderate_review(api_key, grades, review_text) -> bool:
    # Создаем клиента Mistral с переданным API ключом
    client = Mistral(api_key=api_key)

    # Формируем запрос
    response = client.classifiers.moderate_chat(
        model="mistral-moderation-latest",
        inputs=[{"role": "user", "content": review_text}],
    )
    # Вытаскиваем данные с оценкой
    result = response.results[0].category_scores

    # Округляем значения до двух знаков после запятой
    result = {key: round(value, 2) for key, value in result.items()}

    # Словарь под результаты проверки
    checked_result = {}

    for key, value in result.items():
        if key in grades:
            checked_result[key] = value >= grades[key]

    # Если все категории в checked_result имеют значение True, то отзыв проходит модерацию
    return all(checked_result.values())