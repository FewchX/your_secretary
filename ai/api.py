import os
import json
import datetime
import google.generativeai as genai
import asyncio 

genai.configure(api_key="qweasdas") 


# def get_model_with_persona(assistant_name):
#     model_name = "gemini-1.5-flash"
#     system_instruction_text = ""

#     if assistant_name == "1":
#         system_instruction_text = "Ты менеджер-ассистент Неко. Твоя задача — помогать пользователю в организации задач и напоминаниях. "
#     elif assistant_name == "2":
#         system_instruction_text = "Ты собака. Тебя зовут Пуч. Отвечай по-собачьи, иногда используя 'гав' или 'тяф'."
#     else:
#         print("Неверное имя помощника. Используется общий помощник.")
#         system_instruction_text = "Ты полезный AI-помощник."

#     model = genai.GenerativeModel(
#         model_name=model_name,
#         system_instruction=system_instruction_text
#     )
#     return model

async def prompt_decoder(user_message): 
    decoder_model = genai.GenerativeModel('gemini-1.5-flash')

    tomorrow_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    prompt_instruction = f"""
    Извлеки из текста задачу. Сообщение: '{user_message}'.
    Верни результат в формате JSON с полями:
    - 'title': (Обязательное поле) Краткое название задачи. Ты должен сам придумать название задачи, основываясь на сообщении.
    - 'due_date': (Опциональное поле) Дата выполнения задачи в формате ГГГГ-ММ-ДД, если указана. Если нет, оставь пустым.
    - 'category': (Опциональное поле) Категория задачи (например, 'Работа', 'Личное', 'Покупки'), если указана. Если нет, придумай категорию сам на основке сообщения.

    Пример:
    Сообщение: 'Купить молоко к завтрашнему дню'
    JSON: {{"title": "Купить молоко", "due_date": "{tomorrow_date}", "category": "Покупки"}}
    Сообщение: 'Закончить отчет'
    JSON: {{"title": "Закончить отчет", "due_date": "", "category": "Работа"}}
    Сегодня: {datetime.date.today().strftime("%Y-%m-%d")}
    сегодня день недели: {datetime.date.today().strftime("%A")}
    """
    try:
        response = await decoder_model.generate_content_async(prompt_instruction)

        json_output = response.text.strip()

        if json_output.startswith("```json"):
            json_output = json_output[len("```json"):].strip()
        if json_output.endswith("```"):
            json_output = json_output[:-len("```")].strip()

        return json.loads(json_output)
    except json.JSONDecodeError as e:
        print(f"Ошибка при декодировании JSON: {e}")
        raw_response_text = response.text if 'response' in locals() and hasattr(response, 'text') else 'Ответ модели отсутствует или некорректен'
        print(f"Ответ модели: {raw_response_text}")
        return {"error": "Не удалось разобрать JSON из ответа модели", "raw_response": raw_response_text}
    except Exception as e:
        print(f"Произошла другая ошибка: {e}")
        return {"error": str(e)}

async def generate_response(user_message, assistant_name): # Функция асинхронная
    model = get_model_with_persona(assistant_name)
    prompt = f"User: {user_message}\nAssistant:"
    try:
        # *** ИСПРАВЛЕНИЕ ЗДЕСЬ: Используем async_generate_content() ***
        response = await model.generate_content_async(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Произошла ошибка при генерации ответа: {e}")
        return "Извините, я не смог обработать ваш запрос."

# --- АСИНХРОННЫЙ ЗАПУСК КОДА ---
async def main():
    print("--- Тестирование функции prompt_decoder (асинхронно) ---")

    message1 = "Мне нужно на встречу с Димой завтра в 12:40 "
    print(f"\nСообщение: '{message1}'")
    decoded_task1 = await prompt_decoder(message1)
    print(f"Разобранная задача: {json.dumps(decoded_task1, ensure_ascii=False, indent=2)}")

    message2 = "Дедлайн по проекту в следующий понедельник."
    print(f"\nСообщение: '{message2}'")
    decoded_task2 = await prompt_decoder(message2)
    print(f"Разобранная задача: {json.dumps(decoded_task2, ensure_ascii=False, indent=2)}")

    # print("\n--- Тестирование функции generate_response (асинхронно) ---")

    # user_message_cat = "Расскажи что-нибудь интересное."
    # cat_response = await generate_response(user_message_cat, "1")
    # print(f"\nАссистент (Неко): {cat_response}")

    # user_message_dog = "Как ты проводишь свой день?"
    # dog_response = await generate_response(user_message_dog, "2")
    # print(f"\nАссистент (Пуч): {dog_response}")

    # print("\n--- Параллельный запуск нескольких асинхронных запросов ---")
    # tasks = [
    #     prompt_decoder("Заказать билеты на концерт к следующему месяцу."),
    #     generate_response("Кто ты?", "1"),
    #     generate_response("Что ты любишь есть?", "2")
    # ]
    # results = await asyncio.gather(*tasks)

    # print(f"\nРезультат параллельного декодирования: {json.dumps(results[0], ensure_ascii=False, indent=2)}")
    # print(f"\nРезультат параллельного ответа Неко: {results[1]}")
    # print(f"\nРезультат параллельного ответа Пуча: {results[2]}")
    pass


if __name__ == "__main__":
    asyncio.run(main())