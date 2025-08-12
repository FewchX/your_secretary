import json
from datetime import datetime

from db import db_sqlite
from gemini_bot.s_prompts import PROMPTS


def format_tasks_for_prompt(tasks):
    """Преобразует список кортежей задач в JSON для промпта."""
    # Если tasks вернулся как [(id, user_id, title, ...)], то сначала маппим
    tasks_list = []
    for t in tasks:
        tasks_list.append({
            "id": t[0],
            "title": t[2],
            "description": t[3],
            "due_date": t[4],
            "time": t[5],
            "notification_time": t[6],
            "is_recurring": bool(t[7]),
            "recurrence_interval": t[8],
            "is_completed": bool(t[9]),
            "created_at": t[10]
        })
    return json.dumps(tasks_list, ensure_ascii=False)

def prepare_prompt_by_type(prompt_type, user_id, message_text):
    """Автоматически подготавливает промпт по типу задачи."""
    
    current_dt = datetime.now().strftime("%Y-%m-%d %H:%M")
    current_weekday = datetime.now().strftime("%A")  # Monday, Tuesday...
    server_time = current_dt  # то же самое, что datetime.now()
    
    prompt_template = PROMPTS[prompt_type]
    
    # Определяем, нужно ли подгружать задачи
    include_tasks = "{TASKS_JSON}" in prompt_template
    tasks_json = ""
    
    if include_tasks:
        tasks = db_sqlite.get_user_tasks(user_id)
        tasks_json = format_tasks_for_prompt(tasks)
    
    # Подставляем значения
    prompt_filled = prompt_template
    prompt_filled = prompt_filled.replace("{USER_ID}", str(user_id))
    prompt_filled = prompt_filled.replace("{MESSAGE_TEXT}", message_text)
    prompt_filled = prompt_filled.replace("{YYYY-MM-DD HH:MM}", current_dt)
    prompt_filled = prompt_filled.replace("{SERVER_TIME}", server_time)
    prompt_filled = prompt_filled.replace("{CURRENT_WEEKDAY}", current_weekday)
    
    if include_tasks:
        prompt_filled = prompt_filled.replace("{TASKS_JSON}", tasks_json)
    
    return prompt_filled

# Пример использования
# prompt = prepare_prompt_by_type('edit_task', PROMPTS, user_id=5, message_text="перенеси встречу с Петей на пятницу")
# print(prompt)