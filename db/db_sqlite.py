import sqlite3

db = sqlite3.connect('db\database.db')

cursor = db.cursor()
def create_tables():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users(
        id INTEGER PRIMARY KEY,
        telegram_id INTEGER NOT NULL UNIQUE,
        name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP                       
    );""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users(
        id INTEGER PRYMARY KEY,
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

def insert_user(telegram_id, name):
    cursor.execute("INSERT INTO Users (telegram_id, name) VALUES (?, ?)", (telegram_id, name))
    db.commit()

def insert_task(user_id, title, description=None, due_date=None, is_recurring=False, recurrence_interval=None):
    cursor.execute("""
        INSERT INTO Tasks (user_id, title, description, due_date, is_recurring, recurrence_interval)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, title, description, due_date, is_recurring, recurrence_interval))
    db.commit()

def insert_category(name, user_id):
    task = cursor.execute("SELECT id FROM Categories WHERE name = ?", (name,))
    if task == None:
        cursor.execute("INSERT INTO Categories (name, user_id) VALUES (?, ?)", (name, user_id))
        db.commit()
    else:
        print(f"Категория '{name}' уже существует.")
    
def get_user_categories(user_id):
    cursor.execute("SELECT * FROM Categories WHERE user_id = ?", (user_id,))
    return cursor.fetchall()

def get_user_tasks(user_id):
    cursor.execute("SELECT * FROM Tasks WHERE user_id = ?", (user_id,))
    return cursor.fetchall()

def delete_task(task_id):
    cursor.execute("DELETE FROM Tasks WHERE id = ?", (task_id,))
    db.commit()

def delete_category(category_id):
    cursor.execute("DELETE FROM Categories WHERE id = ?", (category_id,))
    db.commit()

def example_user():
    insert_user(123456789, "John Doe")
    insert_category("Work", 1)
    insert_task(1, "Complete project report", "Finish the report by end of the week", "2023-10-31", False, None)


create_tables()
example_user()

db.commit()
db.close()
