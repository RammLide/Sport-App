import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect("sport_tracker.db")
        self.create_tables()
        self.migrate_schema()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY, username TEXT, password TEXT, remember_me INTEGER)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS trainings (
            id INTEGER PRIMARY KEY, user_id INTEGER, date TEXT, type TEXT, duration INTEGER, calories REAL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS exercises (
            id INTEGER PRIMARY KEY,
            training_id INTEGER,
            name TEXT,
            sets INTEGER,
            reps INTEGER,
            weight REAL,
            distance REAL,
            pace REAL,
            FOREIGN KEY (training_id) REFERENCES trainings(id) ON DELETE CASCADE
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS nutrition (
            id INTEGER PRIMARY KEY, user_id INTEGER, date TEXT, meal TEXT, 
            meal_type TEXT,
            calories REAL, protein REAL, fat REAL, carbs REAL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS hydration (
            id INTEGER PRIMARY KEY, user_id INTEGER, date TEXT, amount REAL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS calendar (
            id INTEGER PRIMARY KEY, user_id INTEGER, date TEXT, note TEXT, plan TEXT,
            training_type TEXT, training_duration INTEGER
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY, user_id INTEGER, name TEXT, date TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS training_templates (
            id INTEGER PRIMARY KEY,
            name TEXT,
            type TEXT,
            duration INTEGER,
            calories REAL
        )''')
        cursor.execute("INSERT OR IGNORE INTO training_templates (name, type, duration, calories) VALUES (?, ?, ?, ?)",
                       ("Бег 5 км", "Бег", 30, 300))
        cursor.execute("INSERT OR IGNORE INTO training_templates (name, type, duration, calories) VALUES (?, ?, ?, ?)",
                       ("Силовая базовая", "Силовая", 60, 360))
        self.conn.commit()

    def migrate_schema(self):
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA table_info(calendar)")
        columns = [col[1] for col in cursor.fetchall()]
        if "completed" not in columns:
            cursor.execute("ALTER TABLE calendar ADD COLUMN completed INTEGER DEFAULT 0")
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
                      (user_id, name, datetime.now().strftime("%Y-%m-%d")))
        self.conn.commit()

    def get_training_stats_by_type(self, user_id, start_date, end_date):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT type, SUM(duration), SUM(calories) FROM trainings WHERE user_id = ? AND date BETWEEN ? AND ? GROUP BY type",
            (user_id, start_date, end_date))
        return cursor.fetchall()

    def get_exercise_progress(self, user_id, exercise_name):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT t.date, e.weight, e.sets, e.reps FROM exercises e JOIN trainings t ON e.training_id = t.id WHERE t.user_id = ? AND e.name = ? ORDER BY t.date",
            (user_id, exercise_name))
        return cursor.fetchall()

    def delete_training(self, training_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM trainings WHERE id = ?", (training_id,))
        self.conn.commit()  # Упражнения удалятся автоматически благодаря ON DELETE CASCADE

    def update_training(self, training_id, training_type, duration, calories):
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE trainings SET type = ?, duration = ?, calories = ? WHERE id = ?",
            (training_type, duration, calories, training_id))
        self.conn.commit()

    def delete_exercises(self, training_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM exercises WHERE training_id = ?", (training_id,))
        self.conn.commit()

    def get_training(self, training_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT type, duration, calories FROM trainings WHERE id = ?", (training_id,))
        return cursor.fetchone()

    def get_exercises(self, training_id):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT name, sets, reps, weight, distance, pace FROM exercises WHERE training_id = ?",
            (training_id,))
        return cursor.fetchall()