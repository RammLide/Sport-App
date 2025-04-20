from PySide6.QtWidgets import QWidget, QComboBox, QVBoxLayout, QPushButton, QLineEdit, QLabel, QSizePolicy, QHBoxLayout, QListWidget, QDateEdit, QTabWidget, QMessageBox, QListWidgetItem
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QIcon
from database.db_manager import DatabaseManager
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class HydrationWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = DatabaseManager()
        self.editing_hydration_id = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        self.tabs = QTabWidget()
        self.add_tab = QWidget()
        self.view_tab = QWidget()
        self.edit_tab = QWidget()
        self.analytics_tab = QWidget()
        self.tabs.addTab(self.add_tab, QIcon("icons/hydration.png"), "Добавить воду")
        self.tabs.addTab(self.view_tab, QIcon("icons/view.png"), "Просмотр")
        self.tabs.addTab(self.edit_tab, QIcon("icons/edit.png"), "Редактировать воду")
        self.tabs.addTab(self.analytics_tab, QIcon("icons/analytics.png"), "Аналитика")
        layout.addWidget(self.tabs)


        # Вкладка "Добавить воду"
        add_layout = QVBoxLayout()
        add_layout.setSpacing(10)
        add_layout.setAlignment(Qt.AlignTop)
        title_label = QLabel("Добавить воду")
        title_label.setAccessibleName("header")
        hydration_layout = QHBoxLayout()
        self.amount_input = QLineEdit(self)
        self.amount_input.setPlaceholderText("Объем (мл)")
        self.amount_input.setMinimumWidth(100)
        self.amount_input.setFixedHeight(30)
        hydration_layout.addWidget(QLabel("Объем (мл):"))
        hydration_layout.addWidget(self.amount_input)
        
        add_btn = QPushButton("Добавить воду")
        add_btn.setAccessibleName("action")
        add_btn.setIcon(QIcon("icons/add.png"))
        add_btn.setMinimumWidth(200)
        add_btn.setFixedHeight(30)
        add_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        add_btn.setStyleSheet("""
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
        add_btn.clicked.connect(self.add_hydration)
        add_btn_layout = QHBoxLayout()
        add_btn_layout.addStretch()
        add_btn_layout.addWidget(add_btn)
        add_btn_layout.addStretch()
        
        self.status_label = QLabel("Введите объем воды")
        self.status_label.setAccessibleName("small")
        
        add_layout.addWidget(title_label)
        add_layout.addLayout(hydration_layout)
        add_layout.addLayout(add_btn_layout)
        add_layout.addWidget(self.status_label)
        add_layout.addStretch()
        self.add_tab.setLayout(add_layout)

        # Вкладка "Редактировать воду"
        edit_layout = QVBoxLayout()
        edit_layout.setSpacing(10)
        edit_layout.setAlignment(Qt.AlignTop)
        edit_title_label = QLabel("Редактировать воду")
        edit_title_label.setAccessibleName("header")
        edit_hydration_layout = QHBoxLayout()
        self.edit_amount_input = QLineEdit(self)
        self.edit_amount_input.setPlaceholderText("Объем (мл)")
        self.edit_amount_input.setMinimumWidth(100)
        self.edit_amount_input.setFixedHeight(30)
        edit_hydration_layout.addWidget(QLabel("Объем (мл):"))
        edit_hydration_layout.addWidget(self.edit_amount_input)
        
        save_edit_btn = QPushButton("Сохранить изменения")
        save_edit_btn.setAccessibleName("action")
        save_edit_btn.setIcon(QIcon("icons/save.png"))
        save_edit_btn.setMinimumWidth(200)
        save_edit_btn.setFixedHeight(30)
        save_edit_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        save_edit_btn.setStyleSheet("""
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
        save_edit_btn.clicked.connect(self.save_edited_hydration)
        save_edit_btn_layout = QHBoxLayout()
        save_edit_btn_layout.addStretch()
        save_edit_btn_layout.addWidget(save_edit_btn)
        save_edit_btn_layout.addStretch()
        
        self.edit_status_label = QLabel("Выберите запись для редактирования")
        self.edit_status_label.setAccessibleName("small")
        
        edit_layout.addWidget(edit_title_label)
        edit_layout.addLayout(edit_hydration_layout)
        edit_layout.addLayout(save_edit_btn_layout)
        edit_layout.addWidget(self.edit_status_label)
        edit_layout.addStretch()
        self.edit_tab.setLayout(edit_layout)

        # Вкладка "Просмотр"
        view_layout = QVBoxLayout()
        view_layout.setSpacing(10)
        self.date_selector = QDateEdit(self)
        self.date_selector.setCalendarPopup(True)
        self.date_selector.setDate(QDate.currentDate())
        self.date_selector.dateChanged.connect(self.update_hydration_list)
        self.date_selector.setMinimumWidth(150)
        self.date_selector.setFixedHeight(30)
        self.date_selector.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        self.hydration_list = QListWidget(self)
        self.hydration_list.setMinimumHeight(200)
        self.hydration_list.setStyleSheet("font-size: 14px;")
        self.hydration_list.itemClicked.connect(self.enable_edit_delete_buttons)
        
        nav_layout = QHBoxLayout()
        nav_layout.addStretch()
        prev_btn = QPushButton("Предыдущий день")
        prev_btn.setIcon(QIcon("icons/prev.png"))
        prev_btn.setMinimumWidth(150)
        prev_btn.setFixedHeight(30)
        prev_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        prev_btn.setStyleSheet("""
            QPushButton {
                background-color: #3A3A3A;
                color: #FFFFFF;
                border: 2px solid #00BFFF;
                border-radius: 8px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
            }
            QPushButton:pressed {
                background-color: #2A2A2A;
            }
        """)
        prev_btn.clicked.connect(self.prev_day)
        nav_layout.addWidget(prev_btn)
        
        nav_layout.addWidget(self.date_selector)
        
        next_btn = QPushButton("Следующий день")
        next_btn.setIcon(QIcon("icons/next.png"))
        next_btn.setMinimumWidth(150)
        next_btn.setFixedHeight(30)
        next_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        next_btn.setStyleSheet("""
            QPushButton {
                background-color: #3A3A3A;
                color: #FFFFFF;
                border: 2px solid #00BFFF;
                border-radius: 8px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
            }
            QPushButton:pressed {
                background-color: #2A2A2A;
            }
        """)
        next_btn.clicked.connect(self.next_day)
        nav_layout.addWidget(next_btn)
        nav_layout.addStretch()
        
        action_layout = QHBoxLayout()
        action_layout.addStretch()
        self.edit_btn = QPushButton("Изменить")
        self.edit_btn.setIcon(QIcon("icons/edit.png"))
        self.edit_btn.setMinimumWidth(150)
        self.edit_btn.setFixedHeight(30)
        self.edit_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #3A3A3A;
                color: #FFFFFF;
                border: 2px solid #00BFFF;
                border-radius: 8px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
            }
            QPushButton:pressed {
                background-color: #2A2A2A;
            }
            QPushButton:disabled {
                background-color: #2A2A2A;
                color: #666666;
                border: 2px solid #00BFFF;
            }
        """)
        self.edit_btn.clicked.connect(self.edit_hydration)
        self.edit_btn.setEnabled(False)
        action_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("Удалить")
        self.delete_btn.setIcon(QIcon("icons/delete.png"))
        self.delete_btn.setMinimumWidth(150)
        self.delete_btn.setFixedHeight(30)
        self.delete_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #3A3A3A;
                color: #FFFFFF;
                border: 2px solid #00BFFF;
                border-radius: 8px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
            }
            QPushButton:pressed {
                background-color: #2A2A2A;
            }
            QPushButton:disabled {
                background-color: #2A2A2A;
                color: #666666;
                border: 2px solid #00BFFF;
            }
        """)
        self.delete_btn.clicked.connect(self.delete_hydration)
        self.delete_btn.setEnabled(False)
        action_layout.addWidget(self.delete_btn)
        action_layout.addStretch()
        
        view_layout.addLayout(nav_layout)
        view_layout.addWidget(QLabel("Добавленная вода:"))
        view_layout.addWidget(self.hydration_list)
        view_layout.addLayout(action_layout)
        view_layout.addStretch()
        self.view_tab.setLayout(view_layout)

        # Вкладка "Аналитика"
        analytics_layout = QVBoxLayout()
        analytics_layout.setSpacing(10)
        
        # Добавляем выбор периода
        period_layout = QHBoxLayout()
        period_label = QLabel("Период:")
        period_label.setAccessibleName("small")
        self.period_selector = QComboBox(self)
        self.period_selector.addItems(["Неделя", "Месяц", "Год"])
        self.period_selector.currentTextChanged.connect(self.update_analytics)
        period_layout.addWidget(period_label)
        period_layout.addWidget(self.period_selector)
        period_layout.addStretch()
        analytics_layout.addLayout(period_layout)

        self.figure = plt.Figure(figsize=(14, 6))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setFixedHeight(400)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.stats_label = QLabel("Статистика воды:")
        self.stats_label.setAccessibleName("header")
        analytics_layout.addWidget(self.stats_label)
        analytics_layout.addWidget(self.canvas)
        analytics_layout.addStretch()
        self.analytics_tab.setLayout(analytics_layout)

        self.setLayout(layout)
        self.update_hydration_list()
        self.update_analytics()
        self.check_achievements()

    def update_analytics(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Прозрачный фон
        ax.set_facecolor('none')
        self.figure.set_facecolor('none')
        
        # Настройка осей и тиков
        ax.tick_params(colors='white', labelsize=6)
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Определяем период
        period = self.period_selector.currentText()
        end_date = self.date_selector.date().toString("yyyy-MM-dd")
        if period == "Неделя":
            start_date = self.date_selector.date().addDays(-6).toString("yyyy-MM-dd")
            group_by = "date"
            date_format = "%Y-%m-%d"
            label_format = lambda x: x[-5:]
            title_suffix = "неделю"
        elif period == "Месяц":
            start_date = self.date_selector.date().addDays(-29).toString("yyyy-MM-dd")
            group_by = "strftime('%Y-%W', date)"
            date_format = "%Y-%W"
            label_format = lambda x: f"Неделя {x[-2:]}"
            title_suffix = "месяц"
        else:  # Год
            start_date = self.date_selector.date().addDays(-364).toString("yyyy-MM-dd")
            group_by = "strftime('%Y-%m', date)"
            date_format = "%Y-%m"
            label_format = lambda x: x[-5:]
            title_suffix = "год"

        cursor = self.db.conn.cursor()
        cursor.execute(
            f"""
            SELECT {group_by}, SUM(amount)
            FROM hydration
            WHERE user_id = ? AND date BETWEEN ? AND ?
            GROUP BY {group_by}
            """,
            (self.user["id"], start_date, end_date)
        )
        hydration_data = cursor.fetchall()
        if hydration_data:
            dates = [label_format(row[0]) for row in hydration_data]
            amounts = [row[1] for row in hydration_data]
            x = range(len(dates))
            ax.bar(x, amounts, color="#00C8FF", width=0.5)

            ax.set_xticks(x)
            ax.set_xticklabels(dates, rotation=45, color='white')
            ax.set_title(f"Потребление воды за {title_suffix}", fontsize=8, color='white', pad=15)
            ax.set_ylabel("Объем (мл)", color='white', fontsize=6)
            ax.set_xlabel("Период", color='white', fontsize=6)

            for i, v in enumerate(amounts):
                ax.text(i, v + max(amounts)*0.05, f"{v:.0f}", ha='center', color='white', fontsize=6)

            ax.set_position([0.1, 0.15, 0.75, 0.75])

        else:
            ax.text(0.5, 0.5, "Нет данных", ha='center', va='center', fontsize=8, color='white')

        self.canvas.draw()

        total = self.db.get_hydration_stats(self.user["id"], start_date, end_date)
        profile = self.db.get_user_profile(self.user["id"])
        stats_text = "Статистика воды:\n"
        stats_text += f"Всего за {title_suffix}: {total:.0f} мл\n"
        if profile and profile[0]:
            recommended = profile[0] * 30
            stats_text += f"Рекомендуемая норма: {recommended:.0f} мл/день"
        self.stats_label.setText(stats_text)

    def add_hydration(self):
        amount = self.amount_input.text() or "0"
        date = self.date_selector.date().toString("yyyy-MM-dd")
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Объем должен быть больше 0")
            cursor = self.db.conn.cursor()
            cursor.execute(
                """
                INSERT INTO hydration (user_id, date, amount)
                VALUES (?, ?, ?)
                """,
                (self.user["id"], date, amount)
            )
            self.db.conn.commit()
            self.status_label.setText(f"Добавлено: {amount} мл воды")
            self.amount_input.clear()
            self.update_hydration_list()
            self.update_analytics()
            self.check_achievements()
        except ValueError as e:
            self.status_label.setText(f"Ошибка: {str(e)}")

    def enable_edit_delete_buttons(self):
        self.edit_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)

    def edit_hydration(self):
        selected_items = self.hydration_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для редактирования")
            return
        selected_text = selected_items[0].text()
        amount = float(selected_text.split(" ")[0])
        date = self.date_selector.date().toString("yyyy-MM-dd")
        cursor = self.db.conn.cursor()
        cursor.execute(
            """
            SELECT id, amount
            FROM hydration
            WHERE user_id = ? AND date = ? AND amount = ?
            """,
            (self.user["id"], date, amount)
        )
        hydration = cursor.fetchone()
        if hydration:
            self.editing_hydration_id = hydration[0]
            self.edit_amount_input.setText(str(hydration[1]))
            self.edit_status_label.setText("Редактируйте объем и сохраните")
            self.tabs.setCurrentWidget(self.edit_tab)

    def save_edited_hydration(self):
        if not self.editing_hydration_id:
            self.edit_status_label.setText("Ошибка: выберите запись для редактирования")
            return
        amount = self.edit_amount_input.text() or "0"
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Объем должен быть больше 0")
            cursor = self.db.conn.cursor()
            cursor.execute(
                """
                UPDATE hydration
                SET amount = ?
                WHERE id = ?
                """,
                (amount, self.editing_hydration_id)
            )
            self.db.conn.commit()
            self.edit_status_label.setText(f"Сохранено: {amount} мл воды")
            self.edit_amount_input.clear()
            self.editing_hydration_id = None
            self.update_hydration_list()
            self.update_analytics()
            self.check_achievements()
        except ValueError as e:
            self.edit_status_label.setText(f"Ошибка: {str(e)}")

    def delete_hydration(self):
        selected_items = self.hydration_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для удаления")
            return
        selected_text = selected_items[0].text()
        amount = float(selected_text.split(" ")[0])
        date = self.date_selector.date().toString("yyyy-MM-dd")
        cursor = self.db.conn.cursor()
        cursor.execute(
            """
            SELECT id
            FROM hydration
            WHERE user_id = ? AND date = ? AND amount = ?
            """,
            (self.user["id"], date, amount)
        )
        hydration_id = cursor.fetchone()
        if hydration_id:
            reply = QMessageBox.question(
                self, "Подтверждение", "Удалить эту запись?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                cursor.execute("DELETE FROM hydration WHERE id = ?", (hydration_id[0],))
                self.db.conn.commit()
                self.update_hydration_list()
                self.update_analytics()
                self.edit_btn.setEnabled(False)
                self.delete_btn.setEnabled(False)
                self.status_label.setText("Запись удалена")

    def update_hydration_list(self):
        self.hydration_list.clear()
        date = self.date_selector.date().toString("yyyy-MM-dd")
        cursor = self.db.conn.cursor()
        cursor.execute(
            """
            SELECT amount
            FROM hydration
            WHERE user_id = ? AND date = ?
            """,
            (self.user["id"], date)
        )
        hydration = cursor.fetchall()
        for h in hydration:
            hydration_str = f"{h[0]} мл"
            self.hydration_list.addItem(hydration_str)

    def prev_day(self):
        self.date_selector.setDate(self.date_selector.date().addDays(-1))
        self.update_hydration_list()
        self.update_analytics()

    def next_day(self):
        self.date_selector.setDate(self.date_selector.date().addDays(1))
        self.update_hydration_list()
        self.update_analytics()

    def check_achievements(self):
        cursor = self.db.conn.cursor()
        date = self.date_selector.date().toString("yyyy-MM-dd")
        cursor.execute(
            """
            SELECT SUM(amount)
            FROM hydration
            WHERE user_id = ? AND date = ?
            """,
            (self.user["id"], date)
        )
        daily_total = cursor.fetchone()[0] or 0
        if daily_total >= 2000:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM achievements
                WHERE user_id = ? AND name = ?
                """,
                (self.user["id"], "2 литра воды в день")
            )
            if cursor.fetchone()[0] == 0:
                self.db.add_achievement(self.user["id"], "2 литра воды в день")
                self.status_label.setText("Достижение: 2 литра воды в день!")