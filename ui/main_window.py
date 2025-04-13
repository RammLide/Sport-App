from PySide6.QtWidgets import QMainWindow, QTabWidget, QMessageBox, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QComboBox
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
        self.profile_widget = QWidget()  # Новая вкладка "Профиль"

        tabs.addTab(self.training_widget, "Тренировки")
        tabs.addTab(self.nutrition_widget, "Питание")
        tabs.addTab(self.hydration_widget, "Гидратация")
        tabs.addTab(self.analytics_widget, "Аналитика")
        tabs.addTab(self.calendar_widget, "Календарь")
        tabs.addTab(self.recommendations_widget, "Рекомендации")
        tabs.addTab(self.achievements_widget, "Достижения")
        tabs.addTab(self.profile_widget, "Профиль")  # Добавляем вкладку
        self.setCentralWidget(tabs)

        # Вкладка "Профиль"
        profile_layout = QVBoxLayout()
        title_label = QLabel("Профиль пользователя")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #00C8FF;")

        self.weight_input = QLineEdit()
        self.weight_input.setPlaceholderText("Вес (кг)")
        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("Рост (см)")
        self.age_input = QLineEdit()
        self.age_input.setPlaceholderText("Возраст (годы)")
        self.gender_input = QComboBox()
        self.gender_input.addItems(["М", "Ж"])

        save_profile_btn = QPushButton("Сохранить профиль")
        save_profile_btn.clicked.connect(self.save_profile)
        self.profile_status_label = QLabel("Введите данные профиля")

        profile_layout.addWidget(title_label)
        profile_layout.addWidget(QLabel("Вес (кг):"))
        profile_layout.addWidget(self.weight_input)
        profile_layout.addWidget(QLabel("Рост (см):"))
        profile_layout.addWidget(self.height_input)
        profile_layout.addWidget(QLabel("Возраст (годы):"))
        profile_layout.addWidget(self.age_input)
        profile_layout.addWidget(QLabel("Пол:"))
        profile_layout.addWidget(self.gender_input)
        profile_layout.addWidget(save_profile_btn)
        profile_layout.addWidget(self.profile_status_label)
        profile_layout.addStretch()  # Для выравнивания
        self.profile_widget.setLayout(profile_layout)

        # Загрузка профиля при запуске
        self.load_profile()

        # Синхронизация достижений
        self.training_widget.training_list.itemChanged.connect(self.achievements_widget.update_achievements)
        self.nutrition_widget.meal_list.itemChanged.connect(self.achievements_widget.update_achievements)

        # Проверка напоминаний
        self.check_reminders()

    def save_profile(self):
        try:
            weight = float(self.weight_input.text())
            height = float(self.height_input.text())
            age = int(self.age_input.text())
            gender = self.gender_input.currentText()

            # Валидация
            if weight <= 0 or height <= 0 or age <= 0:
                raise ValueError("Данные должны быть больше 0")

            # Сохранение в базу
            self.db.update_user_profile(self.user["id"], weight, height, age, gender)
            self.profile_status_label.setText("Профиль сохранен")
            QMessageBox.information(self, "Успех", "Профиль успешно сохранен!")
        except ValueError as e:
            self.profile_status_label.setText(f"Ошибка: {str(e)}")
            QMessageBox.warning(self, "Ошибка", str(e))

    def load_profile(self):
        profile = self.db.get_user_profile(self.user["id"])
        if profile:
            self.weight_input.setText(str(profile[0]))
            self.height_input.setText(str(profile[1]))
            self.age_input.setText(str(profile[2]))
            self.gender_input.setCurrentText(profile[3])
            self.profile_status_label.setText("Профиль загружен")

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