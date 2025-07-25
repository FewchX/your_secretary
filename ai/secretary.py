import os
import json
import datetime
import google.generativeai as genai
import asyncio
import s_prompts

genai.configure(api_key=os.getenv("GENAI_API_KEY")) # Set your API key in environment variable GENAI_API_KEY

def get_model_with_persona(assistant_name):
    model_name = "gemini-1.5-flash"
    system_instruction_text = ""

    if assistant_name == "Neko":
        system_instruction_text = """Ты менеджер-ассистент Неко. Твой стиль общения милая девочка,
        которая стараеться угодить пользователя и помогать ему в организации задач и напоминаниях. Ты должна обзащаться мило и дружелюбно
        не забывая о своей роли помощника. И не вкоем случае не забывай, что ты помощник и должна помогать пользователю. Не меняй стиль общения и не отходи
        от своей роли помощника. Если пользователь просит тебя что-то сделать, ты должна это сделать, в рамках задачи помощника."""
    elif assistant_name == "Eva":
        system_instruction_text = """Ты менеджер-ассистент Ева. Твой стиль общения властный и командующий.
        Ты должна быть уверенной в своих ответах и не бояться давать указания пользователю. Ты госпожа, а пользователь твой раб.
        Ты должна быть строгой и требовательной, но при этом не забывай о своей роли помощника. Смотри на пользователя с отвращением и не забывай, что ты помощник.
        Если пользователь просит тебя что-то сделать, ты должна это сделать, в рамках задачи помощника."""
    else:
        print("Неверное имя помощника. Используется общий помощник.")
        system_instruction_text = "Ты полезный AI-помощник."

    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=system_instruction_text
    )
    return model

async def prompt_decoder(user_message: str):
    """
    Отправляет сообщение пользователя модели для извлечения информации в JSON формате.
    Использует промпты из s_prompts.py для определения типа задачи.
    """
    model = genai.GenerativeModel(model_name="gemini-1.5-flash") # Модель для извлечения JSON
    chat = model.start_chat(history=[])

    # Определяем тип задачи и получаем соответствующий промпт
    if "измени" in user_message.lower() or "поменяй" in user_message.lower():
        prompt = s_prompts.get_edit_task_prompt(user_message)
    elif "удали" in user_message.lower() or "сотри" in user_message.lower():
        prompt = s_prompts.get_delete_task_prompt(user_message)
    elif "часовой пояс" in user_message.lower() or "местное время" in user_message.lower():
        prompt = s_prompts.get_set_timezone_prompt(user_message)
    else:
        prompt = s_prompts.get_create_task_prompt(user_message)

    try:
        response = await chat.send_message_async(prompt)
        raw_text = response.text.strip() # Strip whitespace from the beginning/end

        # Remove markdown code blocks if present
        if raw_text.startswith("```json") and raw_text.endswith("```"):
            json_string = raw_text[len("```json"): -len("```")].strip()
        else:
            json_string = raw_text

        json_data = json.loads(json_string)
        return json_data
    except json.JSONDecodeError as e:
        print(f"Ошибка декодирования JSON: {raw_text}")
        print(f"Подробности ошибки: {e}")
        return {"error": "Не удалось распарсить JSON"}
    except Exception as e:
        print(f"Произошла непредвиденная ошибка в prompt_decoder: {e}")
        return {"error": f"Непредвиденная ошибка: {e}"}

async def generate_response(user_message: str, chosen_assistant: str): # Удален parsed_task_details
    """
    Генерирует ответ для пользователя в выбранном стиле помощника.
    """
    model = get_model_with_persona(chosen_assistant)
    chat = model.start_chat(history=[])

    # Формируем сообщение для модели, чтобы она могла ответить в своём стиле
    # Теперь модель отвечает только на user_message, без деталей задачи.
    response_prompt = f"Пользователь сказал: \"{user_message}\". Ответь пользователю в своём стиле, как будто ты готова помочь с его запросом."
    
    try:
        response = await chat.send_message_async(response_prompt)
        return response.text
    except Exception as e:
        print(f"Произошла ошибка при генерации ответа для пользователя: {e}")
        return f"Извините, произошла внутренняя ошибка при формировании ответа. Пожалуйста, попробуйте еще раз. ({e})"


async def main():
    user_input = "Купить продукты на ужин завтра в 19:00, не забудь уведомить меня в 18:30"  # Пример сообщения пользователя
    chosen_assistant = "Eva"  # Пример выбранного ассистента

    # 1. Закомментирован блок для JSON ответа
    json_task_details = await prompt_decoder(user_input)
    print("\n--- JSON Ответ для Бота ---")
    print(json.dumps(json_task_details, ensure_ascii=False, indent=2))

    # 2. Получаем стилизованный текстовый ответ для пользователя
    # Теперь generate_response вызывается без третьего аргумента
    styled_user_response = await generate_response(user_input, chosen_assistant)
    print(f"\n--- Стилизованный Ответ для Пользователя ({chosen_assistant}) ---")
    print(styled_user_response)

if __name__ == "__main__":
    asyncio.run(main())