from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QHBoxLayout
from PySide6.QtCore import QDate
from database.db_manager import DatabaseManager
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class AnalyticsWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = DatabaseManager()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        period_layout = QHBoxLayout()
        self.period_selector = QComboBox(self)
        self.period_selector.addItems(["Неделя", "Месяц", "Год"])
        self.period_selector.currentTextChanged.connect(self.update_analytics)
        period_layout.addWidget(QLabel("Период:"))
        period_layout.addWidget(self.period_selector)
        layout.addLayout(period_layout)

        self.figure = plt.Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        self.update_analytics()
        self.setLayout(layout)

    def update_analytics(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        current_date = QDate.currentDate()
        period = self.period_selector.currentText()

        if period == "Неделя":
            start_date = current_date.addDays(-6).toString("yyyy-MM-dd")
        elif period == "Месяц":
            start_date = current_date.addMonths(-1).toString("yyyy-MM-dd")
        else:  # Год
            start_date = current_date.addYears(-1).toString("yyyy-MM-dd")
        end_date = current_date.toString("yyyy-MM-dd")

        cursor = self.db.conn.cursor()

        # Питание
        cursor.execute(
            "SELECT calories, protein, fat, carbs FROM nutrition WHERE user_id = ? AND date BETWEEN ? AND ?",
            (self.user["id"], start_date, end_date))
        nutrition_data = cursor.fetchall()
        total_calories = sum(row[0] for row in nutrition_data)
        total_protein = sum(row[1] for row in nutrition_data)
        total_fat = sum(row[2] for row in nutrition_data)
        total_carbs = sum(row[3] for row in nutrition_data)

        # Тренировки
        cursor.execute(
            "SELECT calories, duration FROM trainings WHERE user_id = ? AND date BETWEEN ? AND ?",
            (self.user["id"], start_date, end_date))
        training_data = cursor.fetchall()
        total_burned = sum(row[0] for row in training_data)
        total_duration = sum(row[1] for row in training_data)

        ax.bar(["Калории (еда)", "Белки", "Жиры", "Углеводы", "Сожжено", "Длительность (мин)"],
               [total_calories, total_protein, total_fat, total_carbs, total_burned, total_duration])
        ax.set_title(f"Аналитика за {period.lower()}")
        ax.set_ylabel("Значение")
        self.canvas.draw()