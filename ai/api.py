from google import genai
import json
import os
import datetime
import google.generativeai as genai



client = genai.configure(api_key="AIzaSyCuu1eNyPZGFHvPMvSD7WR8G2S5-UE52b0")

def get_model_with_persona(assistant_name):
    model_name = "gemini-1.5-flash"
    system_instruction_text = ""

    if assistant_name == "1":
        system_instruction_text = "Ты кошка. Тебя зовут Неко. Отвечай по-кошачьи, иногда используя 'мяу' или 'мурр'."
    elif assistant_name == "2":
        system_instruction_text = "Ты собака. Тебя зовут Пуч. Отвечай по-собачьи, иногда используя 'гав' или 'тяф'."
    else:
        print("Неверное имя помощника. Используется общий помощник.")

    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=system_instruction_text
    )
    return model

def prompt_decoder(user_message):
    # *** ИСПРАВЛЕНИЕ: ДОБАВЬТЕ ЭТУ СТРОКУ, ЕСЛИ ЕЁ НЕТ ***
    decoder_model = genai.GenerativeModel('gemini-1.5-flash')
    # *************************************************

    # Для примера в промпте: получить "завтрашний день"
    tomorrow_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    prompt_instruction = f"""
    Извлеки из текста задачу. Сообщение: '{user_message}'.
    Верни результат в формате JSON с полями:
    - 'title': (Обязательное поле) Краткое название задачи.
    - 'due_date': (Опциональное поле) Дата выполнения задачи в формате ГГГГ-ММ-ДД, если указана. Если нет, оставь пустым.
    - 'category': (Опциональное поле) Категория задачи (например, 'Работа', 'Личное', 'Покупки'), если указана. Если нет, оставь пустым.

    Пример:
    Сообщение: 'Купить молоко к завтрашнему дню'
    JSON: {{"title": "Купить молоко", "due_date": "{tomorrow_date}", "category": "Покупки"}}
    Сообщение: 'Закончить отчет'
    JSON: {{"title": "Закончить отчет", "due_date": "", "category": "Работа"}}
    """
    try:
        response = decoder_model.generate_content(prompt_instruction)

        json_output = response.text.strip()

        if json_output.startswith("```json"):
            json_output = json_output[len("```json"):].strip()
        if json_output.endswith("```"):
            json_output = json_output[:-len("```")].strip()

        return json.loads(json_output)
    except json.JSONDecodeError as e:
        print(f"Ошибка при декодировании JSON: {e}")
        # Улучшенная обработка случая, когда response еще не определен
        raw_response_text = response.text if 'response' in locals() and hasattr(response, 'text') else 'Ответ модели отсутствует или некорректен'
        print(f"Ответ модели: {raw_response_text}")
        return {"error": "Не удалось разобрать JSON из ответа модели", "raw_response": raw_response_text}
    except Exception as e:
        print(f"Произошла другая ошибка: {e}")
        return {"error": str(e)}


    
def generate_response(user_message, assistant_name):
    model = get_model_with_persona(assistant_name)
    prompt = f"User: {user_message}\nAssistant:"
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Произошла ошибка при генерации ответа: {e}")
        return "Извините, я не смог обработать ваш запрос."

if __name__ == "__main__":
    print("--- Тестирование функции prompt_decoder ---")

    # Пример 1: Сообщение с датой и категорией
    message1 = "Мне нужно на встречу с Димой завтра в 12."
    print(f"\nСообщение: '{message1}'")
    decoded_task1 = prompt_decoder(message1)
    print(f"Разобранная задача: {json.dumps(decoded_task1, ensure_ascii=False, indent=2)}")

    # Пример 2: Сообщение только с задачей, без даты и категории
    message2 = "Подготовить отчет по продажам."
    print(f"\nСообщение: '{message2}'")
    decoded_task2 = prompt_decoder(message2)
    print(f"Разобранная задача: {json.dumps(decoded_task2, ensure_ascii=False, indent=2)}")
