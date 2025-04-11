from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QDateEdit, QLabel
from PySide6.QtCore import QDate
from database.db_manager import DatabaseManager

class CalendarWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = DatabaseManager()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.date_selector = QDateEdit(self)
        self.date_selector.setCalendarPopup(True)
        self.date_selector.setDate(QDate.currentDate())
        self.date_selector.dateChanged.connect(self.load_notes)

        self.note_input = QTextEdit(self)
        self.note_input.setPlaceholderText("Введите заметку...")
        self.plan_input = QTextEdit(self)
        self.plan_input.setPlaceholderText("Введите план на день...")

        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save_notes)

        layout.addWidget(self.date_selector)
        layout.addWidget(QLabel("Заметки:"))
        layout.addWidget(self.note_input)
        layout.addWidget(QLabel("План:"))
        layout.addWidget(self.plan_input)
        layout.addWidget(save_btn)
        self.setLayout(layout)
        self.load_notes()

    def save_notes(self):
        date = self.date_selector.date().toString("yyyy-MM-dd")
        note = self.note_input.toPlainText()
        plan = self.plan_input.toPlainText()
        cursor = self.db.conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO calendar (user_id, date, note, plan) VALUES (?, ?, ?, ?)",
            (self.user["id"], date, note, plan))
        self.db.conn.commit()

    def load_notes(self):
        date = self.date_selector.date().toString("yyyy-MM-dd")
        cursor = self.db.conn.cursor()
        cursor.execute(
            "SELECT note, plan FROM calendar WHERE user_id = ? AND date = ?",
            (self.user["id"], date))
        result = cursor.fetchone()
        if result:
            self.note_input.setText(result[0])
            self.plan_input.setText(result[1])
        else:
            self.note_input.clear()
            self.plan_input.clear()