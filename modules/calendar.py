from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QSizePolicy, QCalendarWidget, QLabel, QComboBox, QLineEdit, QMessageBox, QHBoxLayout, QListWidget, QCheckBox, QListWidgetItem, QScrollArea
from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtGui import QIcon, QTextCharFormat, QColor
from database.db_manager import DatabaseManager

class CalendarWidget(QWidget):
    data_saved = Signal()  # Сигнал, отправляемый после сохранения данных

    def __init__(self, user, update_callback=None):
        super().__init__()
        self.user = user
        self.db = DatabaseManager()
        self.update_callback = update_callback  # Callback для обновления
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

        # Поля для ввода с прокруткой
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #2A2A2A;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #FF9500;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

        inner_widget = QWidget()
        input_layout = QVBoxLayout(inner_widget)
        input_layout.setAlignment(Qt.AlignTop)

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
        save_btn.setIcon(QIcon("icons/save.png"))
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

        # Кнопка для удаления
        self.delete_btn = QPushButton("Удалить")
        self.delete_btn.setMinimumWidth(100)
        self.delete_btn.setFixedHeight(30)
        self.delete_btn.clicked.connect(self.delete_training)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addStretch()
        input_layout.addLayout(btn_layout)

        input_layout.setSpacing(15)
        input_layout.addStretch()  # Добавляем растяжку в конец, чтобы содержимое не растягивалось

        scroll_area.setWidget(inner_widget)
        layout.addWidget(scroll_area)

        layout.setSpacing(15)
        self.setLayout(layout)
        self.highlight_planned_days()  # Выделяем дни с тренировками
        self.load_day_data()

    def save_data(self):
        date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        note = self.note_input.toPlainText()
        plan = self.plan_input.toPlainText()
        training_type = self.training_type.currentText()
        training_duration = self.training_duration.text() or "0"
        try:
            training_duration = int(training_duration)
            if training_type and training_duration <= 0:
                raise ValueError("Длительность должна быть больше 0")
            cursor = self.db.conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO calendar (user_id, date, note, plan, training_type, training_duration, completed)
                VALUES (?, ?, ?, ?, ?, ?, 0)
                """,
                (self.user["id"], date, note, plan, training_type, training_duration)
            )
            self.db.conn.commit()
            self.load_day_data()
            self.training_type.setCurrentIndex(0)
            self.training_duration.clear()
            self.highlight_planned_days()  # Обновляем выделение дней
            self.data_saved.emit()
            if self.update_callback:
                self.update_callback()
            QMessageBox.information(self, "Успех", "Данные сохранены!")
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка: {str(e)}")

    def load_day_data(self):
        date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        cursor = self.db.conn.cursor()
        cursor.execute(
            """
            SELECT note, plan, training_type, training_duration, completed
            FROM calendar WHERE user_id = ? AND date = ?
            """,
            (self.user["id"], date)
        )
        result = cursor.fetchone()
        self.training_list.clear()
        if result:
            self.note_input.setText(result[0] or "")
            self.plan_input.setText(result[1] or "")
            training_type = result[2] or ""
            training_duration = result[3] or 0
            completed = result[4] or 0
            if training_type:
                item = QListWidgetItem(f"{training_type}: {training_duration} мин")
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Checked if completed else Qt.Unchecked)
                item.setData(Qt.UserRole, (date, training_type))
                self.training_list.addItem(item)
        else:
            self.note_input.clear()
            self.plan_input.clear()

    def update_training_completion(self, item):
        date, training_type = item.data(Qt.UserRole)
        completed = 1 if item.checkState() == Qt.Checked else 0
        cursor = self.db.conn.cursor()
        cursor.execute(
            """
            UPDATE calendar SET completed = ? WHERE user_id = ? AND date = ? AND training_type = ?
            """,
            (completed, self.user["id"], date, training_type)
        )
        self.db.conn.commit()
        self.highlight_planned_days()  # Обновляем выделение дней
        self.data_saved.emit()

    def delete_training(self):
        selected_item = self.training_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Ошибка", "Выберите тренировку для удаления")
            return
        _, training_type = selected_item.data(Qt.UserRole)
        date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        reply = QMessageBox.question(
            self, "Подтверждение", "Вы уверены, что хотите удалить эту тренировку?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            cursor = self.db.conn.cursor()
            cursor.execute(
                """
                DELETE FROM calendar WHERE user_id = ? AND date = ? AND training_type = ?
                """,
                (self.user["id"], date, training_type)
            )
            self.db.conn.commit()
            self.load_day_data()
            self.highlight_planned_days()
            self.data_saved.emit()
            QMessageBox.information(self, "Успех", "Тренировка удалена!")

    def highlight_planned_days(self):
        # Сбрасываем форматирование всех дней
        default_format = QTextCharFormat()
        for year in range(self.calendar.yearShown() - 1, self.calendar.yearShown() + 1):
            for month in range(1, 13):
                for day in range(1, 32):
                    date = QDate(year, month, day)
                    if date.isValid():
                        self.calendar.setDateTextFormat(date, default_format)

        # Получаем все запланированные тренировки
        cursor = self.db.conn.cursor()
        cursor.execute(
            """
            SELECT date, completed
            FROM calendar
            WHERE user_id = ? AND training_type IS NOT NULL
            """,
            (self.user["id"],)
        )
        planned_dates = cursor.fetchall()

        # Форматы для выделения
        planned_format = QTextCharFormat()
        planned_format.setBackground(QColor("#90EE90"))  # Светло-зелёный для невыполненных
        completed_format = QTextCharFormat()
        completed_format.setBackground(QColor("#D3D3D3"))  # Светло-серый для выполненных

        for date_str, completed in planned_dates:
            date = QDate.fromString(date_str, "yyyy-MM-dd")
            if date.isValid():
                format_to_apply = completed_format if completed else planned_format
                self.calendar.setDateTextFormat(date, format_to_apply)