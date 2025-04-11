from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QHBoxLayout, QListWidget, QDateEdit
from PySide6.QtCore import QDate
from database.db_manager import DatabaseManager

class HydrationWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = DatabaseManager()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        title_label = QLabel("Добавить воду")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #00C8FF;")
        layout.addWidget(title_label)

        hydration_layout = QHBoxLayout()
        self.amount_input = QLineEdit(self)
        self.amount_input.setPlaceholderText("Объем (мл)")
        hydration_layout.addWidget(self.amount_input)

        add_btn = QPushButton("Добавить воду")
        add_btn.clicked.connect(self.add_hydration)

        self.date_selector = QDateEdit(self)
        self.date_selector.setCalendarPopup(True)
        self.date_selector.setDate(QDate.currentDate())
        self.date_selector.dateChanged.connect(self.update_hydration_list)

        self.hydration_list = QListWidget(self)
        self.hydration_list.setStyleSheet("font-size: 14px;")

        self.status_label = QLabel("Введите объем воды")

        nav_layout = QHBoxLayout()
        prev_btn = QPushButton("Предыдущий день")
        prev_btn.clicked.connect(self.prev_day)
        next_btn = QPushButton("Следующий день")
        next_btn.clicked.connect(self.next_day)
        nav_layout.addWidget(prev_btn)
        nav_layout.addWidget(self.date_selector)
        nav_layout.addWidget(next_btn)

        layout.addLayout(hydration_layout)
        layout.addWidget(add_btn)
        layout.addWidget(self.status_label)
        layout.addLayout(nav_layout)
        layout.addWidget(QLabel("Добавленная вода:"))
        layout.addWidget(self.hydration_list)
        layout.addStretch()
        self.setLayout(layout)

        self.update_hydration_list()

    def add_hydration(self):
        amount = self.amount_input.text() or "0"
        date = self.date_selector.date().toString("yyyy-MM-dd")
        try:
            amount = float(amount)
            self.db.conn.cursor().execute(
                "INSERT INTO hydration (user_id, date, amount) VALUES (?, ?, ?)",
                (self.user["id"], date, amount))
            self.db.conn.commit()
            self.status_label.setText(f"Добавлено: {amount} мл воды")
            self.update_hydration_list()
        except ValueError:
            self.status_label.setText("Ошибка: введите корректное число для объема")

    def update_hydration_list(self):
        self.hydration_list.clear()
        date = self.date_selector.date().toString("yyyy-MM-dd")
        cursor = self.db.conn.cursor()
        cursor.execute(
            "SELECT amount FROM hydration WHERE user_id = ? AND date = ?",
            (self.user["id"], date))
        hydration = cursor.fetchall()
        for h in hydration:
            hydration_str = f"{h[0]} мл"
            self.hydration_list.addItem(hydration_str)

    def prev_day(self):
        self.date_selector.setDate(self.date_selector.date().addDays(-1))
        self.update_hydration_list()

    def next_day(self):
        self.date_selector.setDate(self.date_selector.date().addDays(1))
        self.update_hydration_list()