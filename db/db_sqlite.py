import sqlite3
import os

# Путь к базе данных
db_path = os.path.join('db', 'database.db')

def create_tables():
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users(
        id INTEGER PRIMARY KEY,
        telegram_id INTEGER NOT NULL UNIQUE,
        name TEXT,
        utc_offset TEXT,
        notification_time TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Tasks(
         id INTEGER PRIMARY KEY,
         user_id INTEGER REFERENCES Users(id),
         title TEXT NOT NULL,
         description TEXT,
         due_date TIMESTAMP,
         time TEXT, -- добавлено поле для времени
         notification_time TEXT, -- добавлено поле для времени уведомлений
         is_recurring BOOLEAN DEFAULT FALSE,
         recurrence_interval TEXT,
         is_completed BOOLEAN DEFAULT FALSE,
         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );""")
    # Таблица Categories удалена
    
    db.commit()
    db.close()

def insert_user(telegram_id, name, utc_offset=None, notification_time=None):
    db = sqlite3.connect(db_path)
    cursor = db.cursor()

    try:
        cursor.execute(
            "INSERT INTO Users (telegram_id, name, utc_offset, notification_time) VALUES (?, ?, ?, ?)",
            (telegram_id, name, utc_offset, notification_time)
        )
        db.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        db.close()

def insert_task(user_id, title, description=None, due_date=None, time=None, notification_time=None, is_recurring=False, recurrence_interval=None):
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    
    cursor.execute("""
        INSERT INTO Tasks (user_id, title, description, due_date, time, notification_time, is_recurring, recurrence_interval)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, title, description, due_date, time, notification_time, is_recurring, recurrence_interval))
    db.commit()
    db.close()

def get_user_tasks(user_id):
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    
    cursor.execute("SELECT * FROM Tasks WHERE user_id = ?", (user_id,))
    tasks = cursor.fetchall()
    
    db.close()
    return tasks

def delete_task(task_id):
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    
    cursor.execute("DELETE FROM Tasks WHERE id = ?", (task_id,))
    db.commit()
    db.close()

def get_user_id_by_telegram_id(telegram_id):
    """Получает внутренний ID пользователя по его Telegram ID."""
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    
    cursor.execute("SELECT id FROM Users WHERE telegram_id = ?", (telegram_id,))
    user_id = cursor.fetchone()
    
    db.close()
    
    return user_id[0] if user_id else None

# Вызываем функцию создания таблиц один раз при запуске программы
create_tables()