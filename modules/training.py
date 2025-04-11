from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QHBoxLayout, QComboBox, QListWidget, QDateEdit, QTabWidget
from PySide6.QtCore import QDate
from database.db_manager import DatabaseManager
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class TrainingWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = DatabaseManager()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        tabs = QTabWidget()
        self.add_tab = QWidget()
        self.view_tab = QWidget()
        self.analytics_tab = QWidget()
        tabs.addTab(self.add_tab, "Добавить тренировку")
        tabs.addTab(self.view_tab, "Просмотр")
        tabs.addTab(self.analytics_tab, "Аналитика")
        layout.addWidget(tabs)

        # Вкладка "Добавить тренировку"
        add_layout = QVBoxLayout()
        title_label = QLabel("Добавить тренировку")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #00C8FF;")
        training_layout = QHBoxLayout()
        self.type_input = QComboBox(self)
        self.type_input.addItems([
            "Бег", "Силовая", "Велосипед", "Йога", "Плавание", "Ходьба",
            "Танцы", "Бокс", "Футбол", "Баскетбол", "Теннис", "Гимнастика"
        ])
        self.duration_input = QLineEdit(self)
        self.duration_input.setPlaceholderText("Длительность (мин)")
        self.calories_input = QLineEdit(self)
        self.calories_input.setPlaceholderText("Калории (ккал)")
        training_layout.addWidget(self.type_input)
        training_layout.addWidget(self.duration_input)
        training_layout.addWidget(self.calories_input)
        add_btn = QPushButton("Добавить тренировку")
        add_btn.clicked.connect(self.add_training)
        self.status_label = QLabel("Введите данные тренировки")
        add_layout.addWidget(title_label)
        add_layout.addLayout(training_layout)
        add_layout.addWidget(add_btn)
        add_layout.addWidget(self.status_label)
        self.add_tab.setLayout(add_layout)

        # Вкладка "Просмотр"
        view_layout = QVBoxLayout()
        self.date_selector = QDateEdit(self)
        self.date_selector.setCalendarPopup(True)
        self.date_selector.setDate(QDate.currentDate())
        self.date_selector.dateChanged.connect(self.update_training_list)
        self.training_list = QListWidget(self)
        nav_layout = QHBoxLayout()
        prev_btn = QPushButton("Предыдущий день")
        prev_btn.clicked.connect(self.prev_day)
        next_btn = QPushButton("Следующий день")
        next_btn.clicked.connect(self.next_day)
        nav_layout.addWidget(prev_btn)
        nav_layout.addWidget(self.date_selector)
        nav_layout.addWidget(next_btn)
        view_layout.addLayout(nav_layout)
        view_layout.addWidget(QLabel("Добавленные тренировки:"))
        view_layout.addWidget(self.training_list)
        self.view_tab.setLayout(view_layout)
        self.update_training_list()

        # Вкладка "Аналитика"
        analytics_layout = QVBoxLayout()
        self.figure = plt.Figure()
        self.canvas = FigureCanvas(self.figure)
        analytics_layout.addWidget(self.canvas)
        self.analytics_tab.setLayout(analytics_layout)
        self.update_analytics()

        self.setLayout(layout)

    def add_training(self):
        training_type = self.type_input.currentText()
        duration = self.duration_input.text() or "0"
        calories = self.calories_input.text() or "0"
        date = self.date_selector.date().toString("yyyy-MM-dd")
        try:
            duration = int(duration)
            calories = float(calories)
            self.db.conn.cursor().execute(
                "INSERT INTO trainings (user_id, date, type, duration, calories) VALUES (?, ?, ?, ?, ?)",
                (self.user["id"], date, training_type, duration, calories))
            self.db.conn.commit()
            self.status_label.setText(f"Добавлено: {training_type} ({duration} мин, {calories} ккал)")
            self.update_training_list()
            self.update_analytics()
        except ValueError:
            self.status_label.setText("Ошибка: введите корректные числа для длительности и калорий")

    def update_training_list(self):
        self.training_list.clear()
        date = self.date_selector.date().toString("yyyy-MM-dd")
        cursor = self.db.conn.cursor()
        cursor.execute(
            "SELECT type, duration, calories FROM trainings WHERE user_id = ? AND date = ?",
            (self.user["id"], date))
        trainings = cursor.fetchall()
        for training in trainings:
            training_str = f"{training[0]}: {training[1]} мин, {training[2]} ккал"
            self.training_list.addItem(training_str)

    def prev_day(self):
        self.date_selector.setDate(self.date_selector.date().addDays(-1))
        self.update_training_list()
        self.update_analytics()

    def next_day(self):
        self.date_selector.setDate(self.date_selector.date().addDays(1))
        self.update_training_list()
        self.update_analytics()

    def update_analytics(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        date = self.date_selector.date().toString("yyyy-MM-dd")
        cursor = self.db.conn.cursor()
        cursor.execute(
            "SELECT calories, duration FROM trainings WHERE user_id = ? AND date = ?",
            (self.user["id"], date))
        training_data = cursor.fetchall()
        total_burned = sum(row[0] for row in training_data)
        total_duration = sum(row[1] for row in training_data)

        ax.bar(["Сожжено", "Длительность (мин)"],
               [total_burned, total_duration])
        ax.set_title(f"Тренировки за {date}")
        ax.set_ylabel("Значение")
        self.canvas.draw()