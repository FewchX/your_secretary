import json
import google.generativeai as genai

from gemini_bot_2.prompt_skripts import prepare_prompt_by_type
from db import db_sqlite
from db.db_sqlite import db_path


class Secretary:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def do_this(self, text, chat_id, task):
        try:
            prompt = prepare_prompt_by_type(task, chat_id, text)
            print(f"Processing task '{task}' for chat {chat_id} with prompt: {prompt}")
            response = self.model.generate_content(prompt)
            print("Raw model response:", response.text)
            reply, sql_command = self.analyze_response(response.text)
            if sql_command:
                # Выполняем SQL-команду
                print(f"Executing SQL command: {sql_command}")
                db_sqlite.execute_sql_command(sql_command)
                print("SQL command executed successfully.")

                return reply
            else:
                return "Не удалось сформировать SQL-команду для выполнения."
        except Exception as e:
            print(f"Error processing task '{task}' for chat {chat_id}: {e}")
            return "Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте позже."

    def analyze_response(self, response_text):
        try:
            # Убираем обёртки ```json ... ```
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[len("```json"):].strip()
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3].strip()

            response_json = json.loads(cleaned)
            reply = response_json.get("reply", "")
            sql_command = response_json.get("sql", "")
            return reply, sql_command
        except json.JSONDecodeError as e:
            print("JSON decode error:", e)
            return "Ошибка обработки ответа от модели."
    
    def analyze_message(self, message_text, chat_id):
        try:
            prompt = prepare_prompt_by_type('detect_action', chat_id, message_text)
            response = self.model.generate_content(prompt)
            action_type = response.text.strip()
            print("Action type detected:", action_type)
            if action_type:
                return action_type
            else:
                return "Не удалось определить действие по сообщению."
        except Exception as e:
            print(f"Error analyzing message for chat {chat_id}: {e}")
            return "Произошла ошибка при анализе вашего сообщения. Пожалуйста, попробуйте позже."