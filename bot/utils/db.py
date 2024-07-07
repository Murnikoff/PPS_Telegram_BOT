import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            description TEXT,
            comment TEXT,
            status TEXT DEFAULT 'active',
            start_date TEXT,
            end_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_task(user_id, title, description, comment, start_date, end_date):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tasks (user_id, title, description, comment, start_date, end_date) VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, title, description, comment, start_date, end_date))
    conn.commit()
    conn.close()

def get_active_task(user_id):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, title, description, comment, start_date, end_date FROM tasks WHERE user_id = ? AND status = 'active'
    ''', (user_id,))
    task = cursor.fetchone()
    conn.close()
    return task

def complete_task(task_id, end_date=None):
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE tasks SET status = 'completed', end_date = ? WHERE id = ?
    ''', (end_date, task_id))
    conn.commit()
    conn.close()