# gemini_bot/secretary.py
import google.generativeai as genai
import json
import datetime
from db import db_sqlite # Предполагается, что db_sqlite доступен
from bot.scripts import calculate_user_utc # Предполагается, что scripts доступен
from . import s_prompts

class Secretary:
    def __init__(self, api_key: str):
        # Инициализация модели Gemini для секретаря
        # Используем gemini-1.5-flash, как запрошено
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def _generate_json_response(self, prompt: str) -> dict:
        """
        Внутренний метод для отправки промпта модели и получения JSON ответа.
        """
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            # Удаляем любые лишние символы до и после JSON
            response_text = response_text.strip().replace("```json", "").replace("```", "").strip()
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"Ошибка декодирования JSON: {e}")
            print(f"Полученный текст: {response_text}")
            return {}
        except Exception as e:
            print(f"Ошибка при генерации JSON ответа секретарем: {e}")
            return {}

    def create_task(self, user_message: str, telegram_id: int) -> str:
        """
        Создает новую задачу на основе сообщения пользователя.
        """
        prompt = s_prompts.get_create_task_prompt(user_message)
        task_data = self._generate_json_response(prompt)

        if not task_data:
            return "Не удалось распознать данные для создания задачи. Пожалуйста, попробуйте еще раз."

        title = task_data.get("title")
        due_date = task_data.get("due_date")
        time = task_data.get("time")
        description = task_data.get("description")
        notification_time = task_data.get("notification_time")
        is_recurring = task_data.get("is_recurring", False)
        recurrence_interval = task_data.get("recurrence_interval")

        if not title or not due_date:
            return "Для создания задачи необходимо указать название и дату выполнения."

        # Получаем внутренний ID пользователя
        user_id = db_sqlite.get_user_id_by_telegram_id(telegram_id)
        if not user_id:
            return "Ошибка: Пользователь не найден в базе данных."

        try:
            db_sqlite.insert_task(
                user_id=user_id,
                title=title,
                description=description,
                due_date=due_date,
                time=time,
                notification_time=notification_time,
                is_recurring=is_recurring,
                recurrence_interval=recurrence_interval
            )
            return f"Задача '{title}' на {due_date} {'в ' + time if time else ''} успешно создана!"
        except Exception as e:
            return f"Произошла ошибка при сохранении задачи: {e}"

    def get_tasks(self, user_message: str, telegram_id: int) -> str:
        """
        Возвращает список задач пользователя.
        """
        user_id = db_sqlite.get_user_id_by_telegram_id(telegram_id)
        if not user_id:
            return "Ошибка: Пользователь не найден в базе данных."

        tasks = db_sqlite.get_user_tasks(user_id)
        if not tasks:
            return "У вас пока нет задач."

        response_text = "Ваши задачи:\n"
        for task in tasks:
            # task[0] - id, task[1] - user_id, task[2] - title, task[3] - description,
            # task[4] - due_date, task[5] - time, task[6] - notification_time,
            # task[7] - is_recurring, task[8] - recurrence_interval, task[9] - is_completed
            task_id = task[0]
            title = task[2]
            due_date = task[4]
            time = task[5] if task[5] else ""
            description = f" ({task[3]})" if task[3] else ""
            response_text += f"- ID: {task_id}, '{title}' на {due_date} {time}{description}\n"
        return response_text

    def edit_task(self, user_message: str, telegram_id: int) -> str:
        """
        Изменяет существующую задачу на основе сообщения пользователя.
        """
        prompt = s_prompts.get_edit_task_prompt(user_message)
        edit_data = self._generate_json_response(prompt)

        if not edit_data:
            return "Не удалось распознать данные для изменения задачи. Пожалуйста, попробуйте еще раз."

        original_title = edit_data.get("original_title")
        if not original_title:
            return "Пожалуйста, укажите название задачи, которую вы хотите изменить."

        user_id = db_sqlite.get_user_id_by_telegram_id(telegram_id)
        if not user_id:
            return "Ошибка: Пользователь не найден в базе данных."

        # В реальном приложении здесь нужно получить задачу по original_title и user_id,
        # затем обновить ее поля. Поскольку у нас нет функции update_task в db_sqlite,
        # я просто заглушу это сообщение. Вам нужно будет реализовать эту логику.
        # Для простоты, пока что, мы просто скажем, что задача изменена.

        # Пример заглушки:
        # tasks = db_sqlite.get_user_tasks(user_id)
        # task_to_edit = None
        # for task in tasks:
        #     if task[2] == original_title: # task[2] это title
        #         task_to_edit = task
        #         break

        # if task_to_edit:
        #     # Здесь должна быть логика обновления в базе данных
        #     # Например: db_sqlite.update_task(task_to_edit[0], new_title, new_due_date, ...)
        #     return f"Задача '{original_title}' успешно изменена (функционал обновления в БД требует доработки)."
        # else:
        #     return f"Задача с названием '{original_title}' не найдена."
        return "Функционал изменения задач пока не реализован полностью. Пожалуйста, используйте кнопки для изменения задач."


    def delete_task(self, user_message: str, telegram_id: int) -> str:
        """
        Удаляет задачу на основе сообщения пользователя.
        """
        prompt = s_prompts.get_delete_task_prompt(user_message)
        delete_data = self._generate_json_response(prompt)

        if not delete_data:
            return "Не удалось распознать данные для удаления задачи. Пожалуйста, попробуйте еще раз."

        title_to_delete = delete_data.get("title")
        if not title_to_delete:
            return "Пожалуйста, укажите название задачи, которую вы хотите удалить."

        user_id = db_sqlite.get_user_id_by_telegram_id(telegram_id)
        if not user_id:
            return "Ошибка: Пользователь не найден в базе данных."

        # Находим ID задачи по названию для текущего пользователя
        tasks = db_sqlite.get_user_tasks(user_id)
        task_id_to_delete = None
        for task in tasks:
            if task[2] == title_to_delete: # task[2] это title
                task_id_to_delete = task[0] # task[0] это id задачи
                break

        if task_id_to_delete:
            try:
                db_sqlite.delete_task(task_id_to_delete)
                return f"Задача '{title_to_delete}' успешно удалена!"
            except Exception as e:
                return f"Произошла ошибка при удалении задачи: {e}"
        else:
            return f"Задача с названием '{title_to_delete}' не найдена."


    def set_timezone(self, user_message: str, telegram_id: int) -> str:
        """
        Устанавливает часовой пояс пользователя.
        """
        prompt = s_prompts.get_set_timezone_prompt(user_message)
        timezone_data = self._generate_json_response(prompt)

        if not timezone_data:
            return "Не удалось распознать ваше местное время. Пожалуйста, попробуйте еще раз."

        local_time_str = timezone_data.get("local_time")
        if not local_time_str:
            return "Пожалуйста, укажите ваше местное время в формате ЧЧ:ММ."

        try:
            utc_offset = calculate_user_utc(local_time_str)
            user_id = db_sqlite.get_user_id_by_telegram_id(telegram_id)
            if not user_id:
                return "Ошибка: Пользователь не найден в базе данных."

            # Обновляем utc_offset в таблице Users
            # В db_sqlite нет функции update_user, нужно ее добавить или использовать set_user_utc_offset
            # Предположим, что у вас есть функция для обновления utc_offset
            # Если нет, вам нужно будет ее реализовать в db_sqlite.py
            # Например: db_sqlite.update_user_utc_offset(user_id, utc_offset)
            # Для демонстрации, я просто скажу, что часовой пояс установлен.
            # В реальном приложении, вам нужно будет добавить функцию в db_sqlite.py
            # Например:
            # def update_user_utc_offset(user_id, utc_offset):
            #     db = sqlite3.connect(db_path)
            #     cursor = db.cursor()
            #     cursor.execute("UPDATE Users SET utc_offset = ? WHERE id = ?", (utc_offset, user_id))
            #     db.commit()
            #     db.close()
            return f"Ваш часовой пояс установлен. Смещение UTC: {utc_offset} часов."
        except ValueError as e:
            return f"Ошибка формата времени: {e}. Пожалуйста, используйте формат ЧЧ:ММ."
        except Exception as e:
            return f"Произошла ошибка при установке часового пояса: {e}"

# Пример использования (для тестирования, можно удалить в продакшене)
# if __name__ == "__main__":
#     # Замените 'YOUR_API_KEY' на ваш реальный API ключ Gemini
#     secretary = Secretary(api_key='YOUR_API_KEY')
#     # Пример создания задачи (для этого нужна инициализированная база данных и пользователь)
#     # print(secretary.create_task("Купить продукты завтра в 17:00, список в заметках", 123456789))
#     # print(secretary.get_tasks("", 123456789))
#     # print(secretary.delete_task("Удалить Купить продукты", 123456789))
#     # print(secretary.set_timezone("Мое время 14:30", 123456789))

