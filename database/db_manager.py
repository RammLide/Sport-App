import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect("sport_tracker.db")
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY, username TEXT, password TEXT, remember_me INTEGER)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS trainings (
            id INTEGER PRIMARY KEY, user_id INTEGER, date TEXT, type TEXT, duration INTEGER, calories REAL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS nutrition (
            id INTEGER PRIMARY KEY, user_id INTEGER, date TEXT, meal TEXT, 
            meal_type TEXT,  -- Добавлено новое поле meal_type
            calories REAL, protein REAL, fat REAL, carbs REAL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS hydration (
            id INTEGER PRIMARY KEY, user_id INTEGER, date TEXT, amount REAL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS calendar (
            id INTEGER PRIMARY KEY, user_id INTEGER, date TEXT, note TEXT, plan TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY, user_id INTEGER, name TEXT, date TEXT)''')
        self.conn.commit()

    def add_user(self, username, password, remember_me):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO users (username, password, remember_me) VALUES (?, ?, ?)",
                      (username, password, int(remember_me)))
        self.conn.commit()
        return cursor.lastrowid

    def add_achievement(self, user_id, name):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO achievements (user_id, name, date) VALUES (?, ?, ?)",
                      (user_id, name, datetime.now().strftime("%Y-%m-%d")))  # Исправлен формат даты
        self.conn.commit()