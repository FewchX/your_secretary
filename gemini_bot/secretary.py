import json
import google.generativeai as genai

from gemini_bot.prompt_skripts import prepare_prompt_by_type
from db import db_sqlite


class Secretary:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def do_this(self, text, chat_id, task):
        try:
            prompt = prepare_prompt_by_type(task, chat_id, text)
            print(f"Processing task '{task}' for chat {chat_id} with prompt: {prompt}")
            response = self.model.generate_content(prompt)
            print(56)
            reply, sql_command = self.analyze_response(response.text)
            print(f"Analyzed response - Reply: {reply}, SQL Command: {sql_command}")
            if sql_command:
                # Выполняем SQL-команду
                db_sqlite.execute_sql(sql_command)
                return reply
            else:
                return "Не удалось сформировать SQL-команду для выполнения."
        except Exception as e:
            print(f"Error processing task '{task}' for chat {chat_id}: {e}")
            return "Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте позже."

    def analyze_response(self, response_text):
        """Анализирует ответ от модели и возвращает SQL-команду и ответ пользователю."""
        try:
            print(217)
            response_json = json.loads(response_text)
            reply = response_json.get("reply", "")
            sql_command = response_json.get("sql", "")
            print(f"Response JSON: {response_json}")
            return reply, sql_command
        except json.JSONDecodeError:
            return "Ошибка обработки ответа от модели."
    
    def analyze_message(self, message_text, chat_id):
        try:
            prompt = prepare_prompt_by_type('detect_action', chat_id, message_text)
            print(1)
            response = self.model.generate_content(prompt)
            print(3)
            action_type = response.text.strip()
            print("Action type detected:", action_type)
            print(4)
            if action_type:
                return action_type
            else:
                return "Не удалось определить действие по сообщению."
        except Exception as e:
            print(f"Error analyzing message for chat {chat_id}: {e}")
            return "Произошла ошибка при анализе вашего сообщения. Пожалуйста, попробуйте позже."