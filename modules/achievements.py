from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLabel
from PySide6.QtGui import QIcon, QColor
from PySide6.QtCore import Qt
from database.db_manager import DatabaseManager
from datetime import datetime, timedelta

class AchievementsWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = DatabaseManager()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Заголовок
        title_label = QLabel("Ваши достижения:")
        title_label.setAccessibleName("header")
        layout.addWidget(title_label)

        # Список достижений
        self.achievements_list = QListWidget(self)
        self.achievements_list.setMinimumHeight(300)
        self.achievements_list.setStyleSheet("""
            QListWidget {
                background-color: #2A2A2A;
                border: 1px solid #00C8FF;
                border-radius: 5px;
                color: #FFFFFF;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #444;
            }
            QListWidget::item:hover {
                background-color: #3A3A3A;
            }
        """)
        layout.addWidget(self.achievements_list)

        layout.setSpacing(15)
        self.setLayout(layout)

    def update_achievements(self):
        # Получаем существующие достижения из базы
        cursor = self.db.conn.cursor()
        cursor.execute(
            "SELECT name, date FROM achievements WHERE user_id = ?",
            (self.user["id"],))
        existing_achievements = {name: date for name, date in cursor.fetchall()}

        # Проверяем новые достижения
        self.check_training_streak_achievements(cursor, existing_achievements)
        self.check_total_duration_achievements(cursor, existing_achievements)
        self.check_calories_burned_achievements(cursor, existing_achievements)
        self.check_hydration_achievements(cursor, existing_achievements)
        self.check_distance_achievements(cursor, existing_achievements)

        # Обновляем список достижений
        self.achievements_list.clear()
        cursor.execute(
            "SELECT name, date FROM achievements WHERE user_id = ? ORDER BY date DESC",
            (self.user["id"],))
        achievements = cursor.fetchall()

        if not achievements:
            self.achievements_list.addItem("Нет достижений")
            return

        today = datetime.now().strftime("%Y-%m-%d")
        for name, date in achievements:
            # Определяем иконку и описание в зависимости от типа достижения
            icon_path = "icons/trophy.png"
            description = name
            if "Тренировки подряд" in name:
                icon_path = "icons/streak.png"
                description = f"{name}: Вы тренируетесь регулярно!"
            elif "Минут тренировок" in name:
                icon_path = "icons/time.png"
                description = f"{name}: Отличная работа!"
            elif "Сожжено калорий" in name:
                icon_path = "icons/fire.png"
                description = f"{name}: Вы сжигаете калории как огонь!"
            elif "Литров воды" in name:
                icon_path = "icons/water.png"
                description = f"{name}: Отлично поддерживаете гидратацию!"
            elif "Пройдено км" in name:
                icon_path = "icons/distance.png"
                description = f"{name}: Вы настоящий марафонец!"

            item = QListWidgetItem(QIcon(icon_path), f"{description} (достигнуто: {date})")
            # Если достижение получено сегодня, выделяем его золотым фоном
            if date == today:
                item.setBackground(QColor("#FFD700"))
            self.achievements_list.addItem(item)

    def check_training_streak_achievements(self, cursor, existing):
        # Проверяем регулярность тренировок (5, 10, 15 дней подряд)
        cursor.execute(
            "SELECT date FROM trainings WHERE user_id = ? ORDER BY date",
            (self.user["id"],))
        training_dates = [row[0] for row in cursor.fetchall()]
        training_dates = sorted(set(training_dates))  # Убираем дубликаты

        streak = 1
        max_streak = 1
        if training_dates:
            for i in range(1, len(training_dates)):
                prev_date = datetime.strptime(training_dates[i-1], "%Y-%m-%d")
                curr_date = datetime.strptime(training_dates[i], "%Y-%m-%d")
                if (curr_date - prev_date).days == 1:
                    streak += 1
                    max_streak = max(max_streak, streak)
                else:
                    streak = 1

        streak_achievements = {
            5: "5 тренировок подряд",
            10: "10 тренировок подряд",
            15: "15 тренировок подряд"
        }
        for streak_length, name in streak_achievements.items():
            if max_streak >= streak_length and name not in existing:
                self.db.add_achievement(self.user["id"], name)

    def check_total_duration_achievements(self, cursor, existing):
        # Проверяем общее время тренировок (500, 1000, 2000 минут)
        cursor.execute(
            "SELECT SUM(duration) FROM trainings WHERE user_id = ?",
            (self.user["id"],))
        total_duration = cursor.fetchone()[0] or 0

        duration_achievements = {
            500: "500 минут тренировок",
            1000: "1000 минут тренировок",
            2000: "2000 минут тренировок"
        }
        for duration, name in duration_achievements.items():
            if total_duration >= duration and name not in existing:
                self.db.add_achievement(self.user["id"], name)

    def check_calories_burned_achievements(self, cursor, existing):
        # Проверяем сожжённые калории (5000, 10000, 20000 калорий)
        cursor.execute(
            "SELECT SUM(calories) FROM trainings WHERE user_id = ?",
            (self.user["id"],))
        total_calories = cursor.fetchone()[0] or 0

        calories_achievements = {
            5000: "Сожжено 5000 калорий",
            10000: "Сожжено 10000 калорий",
            20000: "Сожжено 20000 калорий"
        }
        for calories, name in calories_achievements.items():
            if total_calories >= calories and name not in existing:
                self.db.add_achievement(self.user["id"], name)

    def check_hydration_achievements(self, cursor, existing):
        # Проверяем потребление воды (50, 100, 200 литров)
        cursor.execute(
            "SELECT SUM(hydration_amount) FROM calendar WHERE user_id = ?",
            (self.user["id"],))
        total_water = cursor.fetchone()[0] or 0

        hydration_achievements = {
            50: "Выпито 50 литров воды",
            100: "Выпито 100 литров воды",
            200: "Выпито 200 литров воды"
        }
        for liters, name in hydration_achievements.items():
            if total_water >= liters and name not in existing:
                self.db.add_achievement(self.user["id"], name)

    def check_distance_achievements(self, cursor, existing):
        # Проверяем пройденное расстояние (для бега, ходьбы, велосипеда)
        cursor.execute(
            """
            SELECT SUM(te.distance)
            FROM training_exercises te
            JOIN exercises e ON te.exercise_id = e.id
            JOIN training_types tt ON e.type_id = tt.id
            WHERE te.distance IS NOT NULL AND tt.name IN ('Бег', 'Ходьба', 'Велосипед')
            AND te.training_id IN (
                SELECT id FROM trainings WHERE user_id = ?
            )
            """,
            (self.user["id"],))
        total_distance = cursor.fetchone()[0] or 0

        distance_achievements = {
            100: "Пройдено 100 км",
            500: "Пройдено 500 км",
            1000: "Пройдено 1000 км"
        }
        for distance, name in distance_achievements.items():
            if total_distance >= distance and name not in existing:
                self.db.add_achievement(self.user["id"], name)