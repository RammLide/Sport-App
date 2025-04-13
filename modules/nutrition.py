import requests
import hmac
import hashlib
import base64
import time
import random
from urllib.parse import quote
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QHBoxLayout, QComboBox, QListWidget, QDateEdit, QTabWidget, QMessageBox, QFormLayout, QListWidgetItem
from PySide6.QtCore import QTimer, Qt, QThread, Signal, QDate
from googletrans import Translator
from database.db_manager import DatabaseManager
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class SearchThread(QThread):
    search_finished = Signal(list, str)

    def __init__(self, consumer_key, consumer_secret, text, translator):
        super().__init__()
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.text = text
        self.translator = translator
        self._running = True

    def generate_oauth_params(self):
        return {
            "oauth_consumer_key": self.consumer_key,
            "oauth_nonce": str(random.randint(0, 999999999)),
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": str(int(time.time())),
            "oauth_version": "1.0"
        }

    def generate_oauth_signature(self, method, url, params):
        base_string = f"{method}&{quote(url, safe='')}&{quote('&'.join(f'{k}={quote(str(v), safe='')}' for k, v in sorted(params.items())), safe='')}"
        key = f"{self.consumer_secret}&"
        signature = hmac.new(key.encode(), base_string.encode(), hashlib.sha1).digest()
        return base64.b64encode(signature).decode()

    def run(self):
        if not self._running:
            return
        url = "https://platform.fatsecret.com/rest/server.api"
        try:
            search_text = self.translator.translate(self.text, src="ru", dest="en").text if any(c in self.text for c in "абвгдеёжзийклмнопрстуфхцчшщъыьэюя") else self.text
        except Exception:
            search_text = self.text
        params = self.generate_oauth_params()
        params.update({
            "method": "foods.search",
            "search_expression": search_text,
            "format": "json",
            "max_results": 20
        })
        params["oauth_signature"] = self.generate_oauth_signature("GET", url, params)
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            results = response.json().get("foods", {}).get("food", [])
            if not isinstance(results, list):
                results = [results]
            food_list_en = [item["food_name"] for item in results]
            food_list_ru = [self.translator.translate(name, src="en", dest="ru").text for name in food_list_en]
            self.search_finished.emit(food_list_ru, f"Найдено {len(food_list_ru)} продуктов")
        except Exception as e:
            self.search_finished.emit([], f"Ошибка поиска: {str(e)}")

    def stop(self):
        self._running = False
        self.quit()
        self.wait()

class NutritionWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = DatabaseManager()
        self.consumer_key = "bb07e415b6ad4fab8af47074fe0f3464"
        self.consumer_secret = "c944102b4e144af389f554a681b270a4"
        self.translator = Translator()
        self.search_timer = QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        self.search_thread = None
        self.meals = []  # Временный список для добавления еды
        self.editing_meal_id = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.add_tab = QWidget()
        self.view_tab = QWidget()
        self.edit_tab = QWidget()
        self.analytics_tab = QWidget()
        self.tabs.addTab(self.add_tab, "Добавить еду")
        self.tabs.addTab(self.view_tab, "Просмотр")
        self.tabs.addTab(self.edit_tab, "Редактировать еду")
        self.tabs.addTab(self.analytics_tab, "Аналитика")
        layout.addWidget(self.tabs)

        # Вкладка "Добавить еду"
        add_layout = QVBoxLayout()
        title_label = QLabel("Добавить прием пищи")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #00C8FF;")
        meal_layout = QHBoxLayout()
        self.meal_input = QComboBox(self)
        self.meal_input.setEditable(True)
        self.meal_input.setPlaceholderText("Введите еду (например, 'курица')")
        self.meal_input.editTextChanged.connect(self.on_text_changed)
        self.weight_input = QLineEdit(self)
        self.weight_input.setPlaceholderText("Вес (г)")
        meal_layout.addWidget(self.meal_input)
        meal_layout.addWidget(self.weight_input)
        add_btn = QPushButton("Добавить еду")
        add_btn.clicked.connect(self.add_meal)
        self.status_label = QLabel("Начните вводить название еды")
        add_layout.addWidget(title_label)
        add_layout.addLayout(meal_layout)
        add_layout.addWidget(add_btn)
        add_layout.addWidget(self.status_label)
        self.add_tab.setLayout(add_layout)

        # Вкладка "Редактировать еду"
        edit_layout = QVBoxLayout()
        edit_title_label = QLabel("Редактировать прием пищи")
        edit_title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #00C8FF;")
        self.edit_meal_form = QFormLayout()
        self.edit_meal_input = QComboBox(self)
        self.edit_meal_input.setEditable(True)
        self.edit_meal_input.setPlaceholderText("Введите еду")
        self.edit_weight_input = QLineEdit(self)
        self.edit_weight_input.setPlaceholderText("Вес (г)")
        self.edit_meal_form.addRow("Название:", self.edit_meal_input)
        self.edit_meal_form.addRow("Вес (г):", self.edit_weight_input)
        save_edit_btn = QPushButton("Сохранить изменения")
        save_edit_btn.clicked.connect(self.save_edited_meal)
        self.edit_status_label = QLabel("Выберите еду для редактирования")
        edit_layout.addWidget(edit_title_label)
        edit_layout.addLayout(self.edit_meal_form)
        edit_layout.addWidget(save_edit_btn)
        edit_layout.addWidget(self.edit_status_label)
        self.edit_tab.setLayout(edit_layout)

        # Вкладка "Просмотр"
        view_layout = QVBoxLayout()
        self.date_selector = QDateEdit(self)
        self.date_selector.setCalendarPopup(True)
        self.date_selector.setDate(QDate.currentDate())
        self.date_selector.dateChanged.connect(self.update_meal_list)
        self.meal_list = QListWidget(self)
        self.meal_list.itemClicked.connect(self.enable_edit_delete_buttons)
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
        self.edit_btn.clicked.connect(self.edit_meal)
        self.edit_btn.setEnabled(False)
        self.delete_btn = QPushButton("Удалить")
        self.delete_btn.clicked.connect(self.delete_meal)
        self.delete_btn.setEnabled(False)
        action_layout.addWidget(self.edit_btn)
        action_layout.addWidget(self.delete_btn)
        view_layout.addLayout(nav_layout)
        view_layout.addWidget(QLabel("Добавленные продукты:"))
        view_layout.addWidget(self.meal_list)
        view_layout.addLayout(action_layout)
        self.view_tab.setLayout(view_layout)
        self.update_meal_list()

        # Вкладка "Аналитика"
        analytics_layout = QVBoxLayout()
        self.figure = plt.Figure()
        self.canvas = FigureCanvas(self.figure)
        self.stats_label = QLabel("Статистика питания:")
        analytics_layout.addWidget(self.stats_label)
        analytics_layout.addWidget(self.canvas)
        self.analytics_tab.setLayout(analytics_layout)
        self.update_analytics()

        self.setLayout(layout)
        self.check_achievements()

    def on_text_changed(self, text):
        if text and (not self.search_thread or not self.search_thread.isRunning()):
            self.search_timer.start(500)

    def perform_search(self):
        text = self.meal_input.currentText()
        if text:
            self.status_label.setText("Поиск...")
            if self.search_thread and self.search_thread.isRunning():
                self.search_thread.stop()
            self.search_thread = SearchThread(self.consumer_key, self.consumer_secret, text, self.translator)
            self.search_thread.search_finished.connect(self.on_search_finished)
            self.search_thread.start()

    def on_search_finished(self, food_list, status):
        self.meal_input.blockSignals(True)
        self.meal_input.clear()
        if food_list:
            self.meal_input.addItems(food_list)
            self.meal_input.showPopup()
            self.status_label.setText(status)
        else:
            self.status_label.setText(status if "Ошибка" in status else "Ничего не найдено")
        self.meal_input.blockSignals(False)

    def add_meal(self):
        food_name = self.meal_input.currentText()
        weight = self.weight_input.text() or "100"
        date = self.date_selector.date().toString("yyyy-MM-dd")
        if not food_name:
            self.status_label.setText("Выберите еду из списка!")
            return
        try:
            weight = float(weight)
            if weight <= 0:
                raise ValueError("Вес должен быть больше 0")
            calories, protein, fat, carbs = self.get_nutrition_data(food_name, weight)
            if calories == 0:
                self.status_label.setText("Не удалось получить данные о питании")
                return
            cursor = self.db.conn.cursor()
            cursor.execute(
                """
                INSERT INTO nutrition (user_id, date, food_name, calories, protein, fat, carbs)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (self.user["id"], date, f"{food_name} {weight}г", calories, protein, fat, carbs)
            )
            self.db.conn.commit()
            self.status_label.setText(
                f"Добавлено: {food_name} {weight}г "
                f"({calories:.1f} ккал, {protein:.1f}г белка, {fat:.1f}г жиров, {carbs:.1f}г углеводов)"
            )
            self.meal_input.clear()
            self.weight_input.clear()
            self.update_meal_list()
            self.update_analytics()
            self.check_achievements()
        except ValueError as e:
            self.status_label.setText(f"Ошибка: {str(e)}")

    def get_nutrition_data(self, food_name, weight):
        url = "https://platform.fatsecret.com/rest/server.api"
        try:
            food_name_en = self.translator.translate(food_name, src="ru", dest="en").text
        except Exception:
            food_name_en = food_name
        params = self.generate_oauth_params()
        params.update({
            "method": "foods.search",
            "search_expression": food_name_en,
            "format": "json"
        })
        params["oauth_signature"] = self.generate_oauth_signature("GET", url, params)
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            food_data = response.json().get("foods", {}).get("food", [])
            if not food_data:
                return 0, 0, 0, 0
            food_id = food_data[0]["food_id"]
            params = self.generate_oauth_params()
            params.update({
                "method": "food.get.v3",
                "food_id": food_id,
                "format": "json"
            })
            params["oauth_signature"] = self.generate_oauth_signature("GET", url, params)
            response = requests.get(url, params=params)
            response.raise_for_status()
            food_data = response.json()["food"]["servings"]["serving"]
            if not isinstance(food_data, list):
                food_data = [food_data]
            serving = next((s for s in food_data if "metric_serving_amount" in s), food_data[0])
            scale = float(weight) / float(serving["metric_serving_amount"])
            calories = float(serving.get("calories", 0)) * scale
            protein = float(serving.get("protein", 0)) * scale
            fat = float(serving.get("fat", 0)) * scale
            carbs = float(serving.get("carbohydrate", 0)) * scale
            return calories, protein, fat, carbs
        except Exception as e:
            self.status_label.setText(f"Ошибка API: {str(e)}")
            return 0, 0, 0, 0

    def generate_oauth_params(self):
        return {
            "oauth_consumer_key": self.consumer_key,
            "oauth_nonce": str(random.randint(0, 999999999)),
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": str(int(time.time())),
            "oauth_version": "1.0"
        }

    def generate_oauth_signature(self, method, url, params):
        base_string = f"{method}&{quote(url, safe='')}&{quote('&'.join(f'{k}={quote(str(v), safe='')}' for k, v in sorted(params.items())), safe='')}"
        key = f"{self.consumer_secret}&"
        signature = hmac.new(key.encode(), base_string.encode(), hashlib.sha1).digest()
        return base64.b64encode(signature).decode()

    def enable_edit_delete_buttons(self):
        self.edit_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)

    def edit_meal(self):
        selected_items = self.meal_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите еду для редактирования")
            return
        selected_text = selected_items[0].text()
        food_name = selected_text.split(" (")[0]
        date = self.date_selector.date().toString("yyyy-MM-dd")
        cursor = self.db.conn.cursor()
        cursor.execute(
            """
            SELECT id, food_name, calories, protein, fat, carbs
            FROM nutrition
            WHERE user_id = ? AND date = ? AND food_name = ?
            """,
            (self.user["id"], date, food_name)
        )
        meal = cursor.fetchone()
        if meal:
            self.editing_meal_id = meal[0]
            food_name_weight = meal[1].rsplit(" ", 1)
            food_name = food_name_weight[0]
            weight = food_name_weight[1].rstrip("г") if len(food_name_weight) > 1 else "100"
            self.edit_meal_input.setCurrentText(food_name)
            self.edit_weight_input.setText(weight)
            self.edit_status_label.setText("Редактируйте данные и сохраните")
            self.tabs.setCurrentWidget(self.edit_tab)

    def save_edited_meal(self):
        if not self.editing_meal_id:
            self.edit_status_label.setText("Ошибка: выберите еду для редактирования")
            return
        food_name = self.edit_meal_input.currentText()
        weight = self.edit_weight_input.text() or "100"
        if not food_name:
            self.edit_status_label.setText("Введите название еды")
            return
        try:
            weight = float(weight)
            if weight <= 0:
                raise ValueError("Вес должен быть больше 0")
            calories, protein, fat, carbs = self.get_nutrition_data(food_name, weight)
            if calories == 0:
                self.edit_status_label.setText("Не удалось получить данные о питании")
                return
            cursor = self.db.conn.cursor()
            cursor.execute(
                """
                UPDATE nutrition
                SET food_name = ?, calories = ?, protein = ?, fat = ?, carbs = ?
                WHERE id = ?
                """,
                (f"{food_name} {weight}г", calories, protein, fat, carbs, self.editing_meal_id)
            )
            self.db.conn.commit()
            self.edit_status_label.setText(
                f"Сохранено: {food_name} {weight}г "
                f"({calories:.1f} ккал, {protein:.1f}г белка, {fat:.1f}г жиров, {carbs:.1f}г углеводов)"
            )
            self.edit_meal_input.clear()
            self.edit_weight_input.clear()
            self.editing_meal_id = None
            self.update_meal_list()
            self.update_analytics()
            self.check_achievements()
        except ValueError as e:
            self.edit_status_label.setText(f"Ошибка: {str(e)}")

    def delete_meal(self):
        selected_items = self.meal_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите еду для удаления")
            return
        selected_text = selected_items[0].text()
        food_name = selected_text.split(" (")[0]
        date = self.date_selector.date().toString("yyyy-MM-dd")
        cursor = self.db.conn.cursor()
        cursor.execute(
            """
            SELECT id FROM nutrition
            WHERE user_id = ? AND date = ? AND food_name = ?
            """,
            (self.user["id"], date, food_name)
        )
        meal_id = cursor.fetchone()
        if meal_id:
            reply = QMessageBox.question(
                self, "Подтверждение", "Удалить эту еду?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                cursor.execute("DELETE FROM nutrition WHERE id = ?", (meal_id[0],))
                self.db.conn.commit()
                self.update_meal_list()
                self.update_analytics()
                self.edit_btn.setEnabled(False)
                self.delete_btn.setEnabled(False)
                self.status_label.setText("Еда удалена")

    def update_meal_list(self):
        self.meal_list.clear()
        date = self.date_selector.date().toString("yyyy-MM-dd")
        cursor = self.db.conn.cursor()
        cursor.execute(
            """
            SELECT food_name, calories, protein, fat, carbs
            FROM nutrition
            WHERE user_id = ? AND date = ?
            """,
            (self.user["id"], date)
        )
        meals = cursor.fetchall()
        for meal in meals:
            meal_str = (
                f"{meal[0]} ({meal[1]:.1f} ккал, "
                f"{meal[2]:.1f}г белка, {meal[3]:.1f}г жиров, {meal[4]:.1f}г углеводов)"
            )
            self.meal_list.addItem(meal_str)

    def prev_day(self):
        self.date_selector.setDate(self.date_selector.date().addDays(-1))
        self.update_meal_list()
        self.update_analytics()

    def next_day(self):
        self.date_selector.setDate(self.date_selector.date().addDays(1))
        self.update_meal_list()
        self.update_analytics()

    def update_analytics(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        start_date = self.date_selector.date().addDays(-6).toString("yyyy-MM-dd")
        end_date = self.date_selector.date().toString("yyyy-MM-dd")
        cursor = self.db.conn.cursor()
        cursor.execute(
            """
            SELECT date, SUM(calories), SUM(protein), SUM(fat), SUM(carbs)
            FROM nutrition
            WHERE user_id = ? AND date BETWEEN ? AND ?
            GROUP BY date
            """,
            (self.user["id"], start_date, end_date)
        )
        nutrition_data = cursor.fetchall()
        if nutrition_data:
            dates = [row[0][-5:] for row in nutrition_data]
            calories = [row[1] for row in nutrition_data]
            protein = [row[2] for row in nutrition_data]
            fat = [row[3] for row in nutrition_data]
            carbs = [row[4] for row in nutrition_data]
            width = 0.2
            x = range(len(dates))
            ax.bar([i - width*1.5 for i in x], calories, width, label="Калории", color="#00C8FF")
            ax.bar([i - width*0.5 for i in x], protein, width, label="Белки", color="#FF6347")
            ax.bar([i + width*0.5 for i in x], fat, width, label="Жиры", color="#FFD700")
            ax.bar([i + width*1.5 for i in x], carbs, width, label="Углеводы", color="#32CD32")
            ax.set_xticks(x)
            ax.set_xticklabels(dates, rotation=45)
            ax.legend()
            ax.set_title("Питание за неделю")
            ax.set_ylabel("Значение")
            for i, v in enumerate(calories):
                ax.text(i - width*1.5, v + max(calories)*0.01, f"{v:.1f}", ha='center')
        else:
            ax.text(0.5, 0.5, "Нет данных", ha='center', va='center')
        self.figure.tight_layout()
        self.canvas.draw()

        stats = self.db.get_nutrition_stats(self.user["id"], start_date, end_date)
        stats_text = "Статистика питания:\n"
        if stats and any(stats):
            stats_text += (
                f"Калории: {stats[0]:.1f} ккал\n"
                f"Белки: {stats[1]:.1f} г\n"
                f"Жиры: {stats[2]:.1f} г\n"
                f"Углеводы: {stats[3]:.1f} г"
            )
        else:
            stats_text += "Нет данных"
        self.stats_label.setText(stats_text)

    def check_achievements(self):
        cursor = self.db.conn.cursor()
        week_start = self.date_selector.date().addDays(-6).toString("yyyy-MM-dd")
        week_end = self.date_selector.date().toString("yyyy-MM-dd")
        cursor.execute(
            """
            SELECT SUM(calories)
            FROM nutrition
            WHERE user_id = ? AND date BETWEEN ? AND ?
            """,
            (self.user["id"], week_start, week_end)
        )
        total_calories = cursor.fetchone()[0] or 0
        if total_calories >= 10000:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM achievements
                WHERE user_id = ? AND name = ?
                """,
                (self.user["id"], "10000 калорий за неделю")
            )
            if cursor.fetchone()[0] == 0:
                self.db.add_achievement(self.user["id"], "10000 калорий за неделю")
                self.status_label.setText("Достижение: 10000 калорий за неделю!")

        cursor.execute(
            """
            SELECT COUNT(DISTINCT date)
            FROM nutrition
            WHERE user_id = ? AND date BETWEEN ? AND ?
            """,
            (self.user["id"], week_start, week_end)
        )
        nutrition_days = cursor.fetchone()[0] or 0
        if nutrition_days >= 7:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM achievements
                WHERE user_id = ? AND name = ?
                """,
                (self.user["id"], "7 дней питания")
            )
            if cursor.fetchone()[0] == 0:
                self.db.add_achievement(self.user["id"], "7 дней питания")
                self.status_label.setText("Достижение: 7 дней питания!")