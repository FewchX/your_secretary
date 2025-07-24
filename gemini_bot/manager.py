# gemini_bot/manager.py
import google.generativeai as genai
import json
from . import m_prompts
import re

class Manager:
    def __init__(self, api_key: str):
        # Инициализация модели Gemini для менеджера
        # Используем gemini-1.5-flash, как запрошено
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def analyze_message(self, user_message: str) -> str:
        """
        Анализирует сообщение пользователя и определяет тип задачи.
        Возвращает строку с типом действия (например, 'create_task', 'view_tasks', 'unknown').
        """
        prompt = m_prompts.get_manager_prompt(user_message)
        try:
            # Отправляем промпт модели и получаем ответ
            response = self.model.generate_content(prompt)
            # Извлекаем текст ответа
            #print(f"Response from model: {response}")
            response_text = response.text
            response_text = re.sub(r"^```json\s*|\s*```$", "", response_text.strip())
            # Пытаемся распарсить JSON
            action_data = json.loads(response_text)
            return action_data.get("action")
        except Exception as e:
            print(f"Ошибка при анализе сообщения менеджером: {e}")
            return "unknown"

# Пример использования (для тестирования, можно удалить в продакшене)
# if __name__ == "__main__":
#     # Замените 'YOUR_API_KEY' на ваш реальный API ключ Gemini
#     manager = Manager(api_key='YOUR_API_KEY')
#     print(manager.analyze_message("Создай задачу: купить хлеб завтра в 10 утра"))
#     print(manager.analyze_message("Покажи мои задачи"))
#     print(manager.analyze_message("Удалить встречу с Димой"))
#     print(manager.analyze_message("Привет"))

