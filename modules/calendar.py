from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QSizePolicy, QCalendarWidget, QLabel, QComboBox, QLineEdit, QMessageBox, QHBoxLayout, QListWidget, QCheckBox, QListWidgetItem
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QIcon
from database.db_manager import DatabaseManager

class CalendarWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = DatabaseManager()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Заголовок
        title_label = QLabel("Календарь и планирование")
        title_label.setAccessibleName("header")
        layout.addWidget(title_label)
        
        # Визуальный календарь
        self.calendar = QCalendarWidget(self)
        self.calendar.setSelectedDate(QDate.currentDate())
        self.calendar.selectionChanged.connect(self.load_day_data)
        layout.addWidget(self.calendar)
        
        # Поля для ввода
        input_layout = QVBoxLayout()
        
        # Заметки
        note_label = QLabel("Заметки:")
        note_label.setAccessibleName("small")
        self.note_input = QTextEdit(self)
        self.note_input.setPlaceholderText("Введите заметку...")
        self.note_input.setMinimumHeight(80)
        input_layout.addWidget(note_label)
        input_layout.addWidget(self.note_input)
        
        # План
        plan_label = QLabel("План:")
        plan_label.setAccessibleName("small")
        self.plan_input = QTextEdit(self)
        self.plan_input.setPlaceholderText("Введите план на день...")
        self.plan_input.setMinimumHeight(80)
        input_layout.addWidget(plan_label)
        input_layout.addWidget(self.plan_input)
        
        # Тренировка
        training_label = QLabel("Добавить тренировку:")
        training_label.setAccessibleName("small")
        input_layout.addWidget(training_label)
        
        training_layout = QHBoxLayout()
        self.training_type = QComboBox(self)
        self.training_type.addItems(["", "Бег", "Силовая", "Велосипед", "Плавание", "Ходьба", "Бокс", "Теннис", "Гимнастика"])
        self.training_type.setMinimumWidth(150)
        self.training_type.setFixedHeight(30)
        self.training_duration = QLineEdit(self)
        self.training_duration.setPlaceholderText("Длительность (мин)")
        self.training_duration.setMinimumWidth(150)
        self.training_duration.setFixedHeight(30)
        training_layout.addWidget(self.training_type)
        training_layout.addWidget(self.training_duration)
        input_layout.addLayout(training_layout)
        
        # Кнопка сохранения
        save_btn = QPushButton("Сохранить")
        save_btn.setAccessibleName("action")
        save_btn.setIcon(QIcon("icons/save.png"))  # Иконка для сохранения
        save_btn.setMinimumWidth(200)
        save_btn.setFixedHeight(30)
        save_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9500;
                color: #FFFFFF;
                border-radius: 8px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #E68A00;
            }
            QPushButton:pressed {
                background-color: #CC7700;
            }
        """)
        save_btn.clicked.connect(self.save_data)
        # Центрируем кнопку
        save_btn_layout = QHBoxLayout()
        save_btn_layout.addStretch()
        save_btn_layout.addWidget(save_btn)
        save_btn_layout.addStretch()
        input_layout.addLayout(save_btn_layout)
        
        # Список тренировок
        training_list_label = QLabel("Запланированные тренировки:")
        training_list_label.setAccessibleName("small")
        self.training_list = QListWidget(self)
        self.training_list.setMinimumHeight(100)
        self.training_list.itemChanged.connect(self.update_training_completion)
        input_layout.addWidget(training_list_label)
        input_layout.addWidget(self.training_list)
        
        input_layout.setSpacing(15)
        layout.addLayout(input_layout)
        
        layout.setSpacing(15)
        self.setLayout(layout)
        self.load_day_data()

    def save_data(self):
        date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        note = self.note_input.toPlainText()
        plan = self.plan_input.toPlainText()
        training_type = self.training_type.currentText()
        training_duration = self.training_duration.text() or "0"
        try:
            training_duration = int(training_duration)
            cursor = self.db.conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO calendar (user_id, date, note, plan, training_type, training_duration, completed) VALUES (?, ?, ?, ?, ?, ?, 0)",
                (self.user["id"], date, note, plan, training_type, training_duration))
            self.db.conn.commit()
            self.load_day_data()
            self.training_type.setCurrentIndex(0)
            self.training_duration.clear()
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите корректную длительность")

    def load_day_data(self):
        date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        cursor = self.db.conn.cursor()
        cursor.execute(
            "SELECT note, plan, training_type, training_duration, completed FROM calendar WHERE user_id = ? AND date = ?",
            (self.user["id"], date))
        result = cursor.fetchone()
        if result:
            self.note_input.setText(result[0])
            self.plan_input.setText(result[1])
            training_type = result[2] or ""
            training_duration = result[3] or 0
            completed = result[4]
        else:
            self.note_input.clear()
            self.plan_input.clear()
            training_type = ""
            training_duration = 0
            completed = 0
        
        self.training_list.clear()
        if training_type:
            item = QListWidgetItem(f"{training_type}: {training_duration} мин")
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if completed else Qt.Unchecked)
            item.setData(Qt.UserRole, date)
            self.training_list.addItem(item)

    def update_training_completion(self, item):
        date = item.data(Qt.UserRole)
        completed = 1 if item.checkState() == Qt.Checked else 0
        cursor = self.db.conn.cursor()
        cursor.execute(
            "UPDATE calendar SET completed = ? WHERE user_id = ? AND date = ?",
            (completed, self.user["id"], date))
        self.db.conn.commit()