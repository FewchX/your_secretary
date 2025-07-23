import sqlite3
import os

# Путь к базе данных
db_path = os.path.join('db', 'db/database.db')

def create_tables():
    # Создаем соединение и курсор внутри функции
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    
    # Зачем-то два раза создаешь таблицу Users, я оставляю один
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users(
        id INTEGER PRIMARY KEY,
        telegram_id INTEGER NOT NULL UNIQUE,
        name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Tasks(
         id INTEGER PRIMARY KEY,
         user_id INTEGER REFERENCES Users(id),
         title TEXT NOT NULL,
         description TEXT,
         due_date TIMESTAMP,
         is_recurring BOOLEAN DEFAULT FALSE,
         recurrence_interval TEXT,
         is_completed BOOLEAN DEFAULT FALSE,
         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Categories(
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        user_id INTEGER REFERENCES Users(id)
    );""")
    
    db.commit()
    db.close()

def insert_user(telegram_id, name):
    # Создаем соединение и курсор внутри функции
    db = sqlite3.connect(db_path)
    cursor = db.cursor()

    try:
        cursor.execute("INSERT INTO Users (telegram_id, name) VALUES (?, ?)", (telegram_id, name))
        db.commit()
    except sqlite3.IntegrityError:
        # Если пользователь уже существует (telegram_id - UNIQUE), ничего не делаем
        pass
    finally:
        db.close()

def insert_task(user_id, title, description=None, due_date=None, is_recurring=False, recurrence_interval=None):
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    
    cursor.execute("""
        INSERT INTO Tasks (user_id, title, description, due_date, is_recurring, recurrence_interval)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, title, description, due_date, is_recurring, recurrence_interval))
    db.commit()
    db.close()

def insert_category(name, user_id):
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    
    cursor.execute("SELECT id FROM Categories WHERE name = ? AND user_id = ?", (name, user_id))
    task = cursor.fetchone()
    
    if task is None:
        cursor.execute("INSERT INTO Categories (name, user_id) VALUES (?, ?)", (name, user_id))
        db.commit()
    else:
        print(f"Категория '{name}' уже существует.")
    
    db.close()
    
def get_user_categories(user_id):
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    
    cursor.execute("SELECT * FROM Categories WHERE user_id = ?", (user_id,))
    categories = cursor.fetchall()
    
    db.close()
    return categories

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

def delete_category(category_id):
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    
    cursor.execute("DELETE FROM Categories WHERE id = ?", (category_id,))
    db.commit()
    db.close()

# Вызываем функцию создания таблиц один раз при запуске программы
create_tables()