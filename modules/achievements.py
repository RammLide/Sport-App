from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLabel
from database.db_manager import DatabaseManager

class AchievementsWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = DatabaseManager()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Ваши достижения:"))
        self.achievements_list = QListWidget(self)
        layout.addWidget(self.achievements_list)
        self.update_achievements()
        self.setLayout(layout)

    def update_achievements(self):
        self.achievements_list.clear()
        cursor = self.db.conn.cursor()
        cursor.execute(
            "SELECT name, date FROM achievements WHERE user_id = ?",
            (self.user["id"],))
        achievements = cursor.fetchall()
        for name, date in achievements:
            self.achievements_list.addItem(f"{name} - {date}")