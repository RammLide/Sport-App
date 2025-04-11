from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import QDate
from database.db_manager import DatabaseManager

class RecommendationsWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = DatabaseManager()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.advice_label = QLabel("Совет от AI: Загрузите данные для анализа")
        layout.addWidget(self.advice_label)
        self.update_recommendations()
        self.setLayout(layout)

    def update_recommendations(self):
        date = QDate.currentDate().toString("yyyy-MM-dd")
        cursor = self.db.conn.cursor()

        cursor.execute(
            "SELECT calories FROM nutrition WHERE user_id = ? AND date = ?",
            (self.user["id"], date))
        nutrition_data = cursor.fetchall()
        total_calories = sum(row[0] for row in nutrition_data)

        cursor.execute(
            "SELECT calories, duration FROM trainings WHERE user_id = ? AND date = ?",
            (self.user["id"], date))
        training_data = cursor.fetchall()
        total_burned = sum(row[0] for row in training_data)
        total_duration = sum(row[1] for row in training_data)

        advice = self.get_ai_advice(total_calories, total_burned, total_duration)
        self.advice_label.setText(f"Совет от AI: {advice}")

    def get_ai_advice(self, calories_in, calories_burned, duration):
        if not calories_in and not calories_burned:
            return "Добавьте еду и тренировки для анализа."
        balance = calories_in - calories_burned
        if balance > 500:
            return "Вы потребляете больше калорий, чем сжигаете. Увеличьте длительность тренировок."
        elif balance < -500:
            return "Вы сжигаете больше, чем потребляете. Добавьте больше еды в рацион."
        elif duration < 30:
            return "Тренировки слишком короткие. Постарайтесь заниматься хотя бы 30 минут."
        else:
            return "Хороший баланс калорий и тренировок. Продолжайте в том же духе!"