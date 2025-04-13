from PySide6.QtWidgets import QMainWindow, QTabWidget, QMessageBox
from modules.training import TrainingWidget
from modules.nutrition import NutritionWidget
from modules.hydration import HydrationWidget
from modules.analytics import AnalyticsWidget
from modules.calendar import CalendarWidget
from modules.recommendations import RecommendationsWidget
from modules.achievements import AchievementsWidget
from PySide6.QtCore import QDate
from database.db_manager import DatabaseManager

class MainWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = DatabaseManager()
        self.setWindowTitle("Sport Tracker")
        self.setGeometry(100, 100, 1200, 800)
        self.init_ui()

    def init_ui(self):
        tabs = QTabWidget()
        self.training_widget = TrainingWidget(self.user)
        self.nutrition_widget = NutritionWidget(self.user)
        self.hydration_widget = HydrationWidget(self.user)
        self.analytics_widget = AnalyticsWidget(self.user)
        self.calendar_widget = CalendarWidget(self.user)
        self.recommendations_widget = RecommendationsWidget(self.user)
        self.achievements_widget = AchievementsWidget(self.user)

        tabs.addTab(self.training_widget, "Тренировки")
        tabs.addTab(self.nutrition_widget, "Питание")
        tabs.addTab(self.hydration_widget, "Гидратация")
        tabs.addTab(self.analytics_widget, "Аналитика")
        tabs.addTab(self.calendar_widget, "Календарь")
        tabs.addTab(self.recommendations_widget, "Рекомендации")
        tabs.addTab(self.achievements_widget, "Достижения")
        self.setCentralWidget(tabs)

        # Синхронизация достижений
        self.training_widget.training_list.itemChanged.connect(self.achievements_widget.update_achievements)
        self.nutrition_widget.meal_list.itemChanged.connect(self.achievements_widget.update_achievements)

        # Проверка напоминаний
        self.check_reminders()

    def check_reminders(self):
        cursor = self.db.conn.cursor()
        today = QDate.currentDate().toString("yyyy-MM-dd")
        cursor.execute(
            "SELECT training_type, training_duration FROM calendar WHERE user_id = ? AND date = ? AND completed = 0",
            (self.user["id"], today))
        reminders = cursor.fetchall()
        for reminder in reminders:
            if reminder[0]:
                QMessageBox.information(self, "Напоминание", f"Сегодня: {reminder[0]} ({reminder[1]} мин)")