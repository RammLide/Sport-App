from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QHBoxLayout, QListWidget, QDateEdit, QTabWidget, QMessageBox, QListWidgetItem
from PySide6.QtCore import QDate
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
        layout.setSpacing(10)
        self.tabs = QTabWidget()
        self.add_tab = QWidget()
        self.view_tab = QWidget()
        self.edit_tab = QWidget()
        self.analytics_tab = QWidget()
        self.tabs.addTab(self.add_tab, "Добавить воду")
        self.tabs.addTab(self.view_tab, "Просмотр")
        self.tabs.addTab(self.edit_tab, "Редактировать воду")
        self.tabs.addTab(self.analytics_tab, "Аналитика")
        layout.addWidget(self.tabs)

        # Вкладка "Добавить воду"
        add_layout = QVBoxLayout()
        title_label = QLabel("Добавить воду")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #00C8FF;")
        hydration_layout = QHBoxLayout()
        self.amount_input = QLineEdit(self)
        self.amount_input.setPlaceholderText("Объем (мл)")
        hydration_layout.addWidget(self.amount_input)
        add_btn = QPushButton("Добавить воду")
        add_btn.clicked.connect(self.add_hydration)
        self.status_label = QLabel("Введите объем воды")
        add_layout.addWidget(title_label)
        add_layout.addLayout(hydration_layout)
        add_layout.addWidget(add_btn)
        add_layout.addWidget(self.status_label)
        self.add_tab.setLayout(add_layout)

        # Вкладка "Редактировать воду"
        edit_layout = QVBoxLayout()
        edit_title_label = QLabel("Редактировать воду")
        edit_title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #00C8FF;")
        edit_hydration_layout = QHBoxLayout()
        self.edit_amount_input = QLineEdit(self)
        self.edit_amount_input.setPlaceholderText("Объем (мл)")
        edit_hydration_layout.addWidget(self.edit_amount_input)
        save_edit_btn = QPushButton("Сохранить изменения")
        save_edit_btn.clicked.connect(self.save_edited_hydration)
        self.edit_status_label = QLabel("Выберите запись для редактирования")
        edit_layout.addWidget(edit_title_label)
        edit_layout.addLayout(edit_hydration_layout)
        edit_layout.addWidget(save_edit_btn)
        edit_layout.addWidget(self.edit_status_label)
        self.edit_tab.setLayout(edit_layout)

        # Вкладка "Просмотр"
        view_layout = QVBoxLayout()
        self.date_selector = QDateEdit(self)
        self.date_selector.setCalendarPopup(True)
        self.date_selector.setDate(QDate.currentDate())
        self.date_selector.dateChanged.connect(self.update_hydration_list)
        self.hydration_list = QListWidget(self)
        self.hydration_list.setStyleSheet("font-size: 14px;")
        self.hydration_list.itemClicked.connect(self.enable_edit_delete_buttons)
        nav_layout = QHBoxLayout()
        prev_btn = QPushButton("Предыдущий день")
        prev_btn.clicked.connect(self.prev_day)
        next_btn = QPushButton("Следующий день")
        next_btn.clicked.connect(self.next_day)
        nav_layout.addWidget(prev_btn)
        nav_layout.addWidget(self.date_selector)
        nav_layout.addWidget(next_btn)
        action_layout = QHBoxLayout()
        self.edit_btn = QPushButton("Изменить")
        self.edit_btn.clicked.connect(self.edit_hydration)
        self.edit_btn.setEnabled(False)
        self.delete_btn = QPushButton("Удалить")
        self.delete_btn.clicked.connect(self.delete_hydration)
        self.delete_btn.setEnabled(False)
        action_layout.addWidget(self.edit_btn)
        action_layout.addWidget(self.delete_btn)
        view_layout.addLayout(nav_layout)
        view_layout.addWidget(QLabel("Добавленная вода:"))
        view_layout.addWidget(self.hydration_list)
        view_layout.addLayout(action_layout)
        self.view_tab.setLayout(view_layout)

        # Вкладка "Аналитика"
        analytics_layout = QVBoxLayout()
        self.figure = plt.Figure()
        self.canvas = FigureCanvas(self.figure)
        self.stats_label = QLabel("Статистика воды:")
        analytics_layout.addWidget(self.stats_label)
        analytics_layout.addWidget(self.canvas)
        self.analytics_tab.setLayout(analytics_layout)

        self.setLayout(layout)
        self.update_hydration_list()
        self.update_analytics()
        self.check_achievements()

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

    def update_analytics(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        start_date = self.date_selector.date().addDays(-6).toString("yyyy-MM-dd")
        end_date = self.date_selector.date().toString("yyyy-MM-dd")
        cursor = self.db.conn.cursor()
        cursor.execute(
            """
            SELECT date, SUM(amount)
            FROM hydration
            WHERE user_id = ? AND date BETWEEN ? AND ?
            GROUP BY date
            """,
            (self.user["id"], start_date, end_date)
        )
        hydration_data = cursor.fetchall()
        if hydration_data:
            dates = [row[0][-5:] for row in hydration_data]
            amounts = [row[1] for row in hydration_data]
            ax.bar(dates, amounts, color="#00C8FF")
            ax.set_title("Потребление воды за неделю")
            ax.set_ylabel("Объем (мл)")
            ax.set_xlabel("Дата")
            for i, v in enumerate(amounts):
                ax.text(i, v + max(amounts)*0.01, f"{v:.0f}", ha='center')
        else:
            ax.text(0.5, 0.5, "Нет данных", ha='center', va='center')
        self.figure.tight_layout()
        self.canvas.draw()

        total = self.db.get_hydration_stats(self.user["id"], start_date, end_date)
        profile = self.db.get_user_profile(self.user["id"])
        stats_text = "Статистика воды:\n"
        stats_text += f"Всего за неделю: {total:.0f} мл\n"
        if profile and profile[0]:
            recommended = profile[0] * 30  # 30 мл/кг
            stats_text += f"Рекомендуемая норма: {recommended:.0f} мл/день"
        self.stats_label.setText(stats_text)

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