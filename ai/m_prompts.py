import json
import google.generativeai as genai
import asyncio 

import os

genai.configure(api_key=os.getenv("GENAI_API_KEY"))

async def manager_prompts(user_message: str) -> dict:
    """
    Классифицирует намерение пользователя на основе его сообщения
    и возвращает действие в формате JSON.
    """
    model_name = "gemini-1.5-flash"
    
    system_instruction_text = """Ты - менеджер по планированию задач. Твоя задача - определить намерение пользователя
    и вернуть одно из следующих действий в формате JSON:

    - "create_task": Пользователь хочет создать новую задачу.
    - "view_tasks": Пользователь хочет просмотреть свои задачи.
    - "edit_task": Пользователь хочет изменить существующую задачу.
    - "delete_task": Пользователь хочет удалить задачу.
    - "select_timezone": Пользователь хочет выбрать или изменить свой часовой пояс.
    - "help": Пользователь запрашивает помощь или информацию о командах.
    - "unknown": Если запрос пользователя не соответствует ни одному из известных действий.

    Твой ответ должен быть только в формате JSON, содержащим поле "action".
    Пример: {"action": "create_task"}
    Пример: {"action": "view_tasks"}
    Пример: {"action": "unknown"}
    """
    
    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=system_instruction_text
    )

    try:
        response = await model.generate_content_async(user_message)
        
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
        return {"action": "unknown", "error": "Не удалось разобрать JSON из ответа модели", "raw_response": raw_response_text}
    except Exception as e:
        print(f"Произошла другая ошибка при классификации намерения: {e}")
        return {"action": "unknown", "error": str(e)}

async def main():
    print("--- Тестирование функции manager_prompts ---")

    test_messages = [
        "Создай новую задачу: купить хлеб",
        "Покажи все мои задачи",
        "Измени задачу 'позвонить маме'",
        "Удали задачу 'отправить письмо'",
        "Хочу поменять часовой пояс на московский",
        "Помощь",
        "Что ты умеешь?",
        "Привет, как дела?"
    ]

    for msg in test_messages:
        print(f"\nСообщение пользователя: '{msg}'")
        action_result = await manager_prompts(msg)
        print(f"Определенное действие: {json.dumps(action_result, ensure_ascii=False, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main())
