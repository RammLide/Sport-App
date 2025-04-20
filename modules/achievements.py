
from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLabel
from PySide6.QtGui import QIcon
from database.db_manager import DatabaseManager

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
        
        self.achievements_list = QListWidget(self)
        self.achievements_list.setMinimumHeight(200)  # Даём больше пространства для списка
        layout.addWidget(self.achievements_list)
        
        self.update_achievements()
        
        layout.setSpacing(15)  # Увеличиваем отступы
        self.setLayout(layout)

    def update_achievements(self):
        self.achievements_list.clear()
        cursor = self.db.conn.cursor()
        cursor.execute(
            "SELECT name, date FROM achievements WHERE user_id = ?",
            (self.user["id"],))
        achievements = cursor.fetchall()
        if not achievements:
            self.achievements_list.addItem("Нет достижений")
        else:
            for name, date in achievements:
                item = f"{name} - {date}"
                self.achievements_list.addItem(item)
        cursor.close()