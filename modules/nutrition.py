import requests
import hmac
import hashlib
import base64
import time
import random
from urllib.parse import quote
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QHBoxLayout, QComboBox, QListWidget, QDateEdit, QTabWidget
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
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        tabs = QTabWidget()
        self.add_tab = QWidget()
        self.view_tab = QWidget()
        self.analytics_tab = QWidget()
        tabs.addTab(self.add_tab, "Добавить еду")
        tabs.addTab(self.view_tab, "Просмотр")
        tabs.addTab(self.analytics_tab, "Аналитика")
        layout.addWidget(tabs)

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
        self.meal_type = QComboBox(self)
        self.meal_type.addItems(["Завтрак", "Обед", "Ужин", "Перекус"])
        meal_layout.addWidget(self.meal_input)
        meal_layout.addWidget(self.weight_input)
        meal_layout.addWidget(self.meal_type)
        add_btn = QPushButton("Добавить еду")
        add_btn.clicked.connect(self.add_meal)
        self.status_label = QLabel("Начните вводить название еды")
        add_layout.addWidget(title_label)
        add_layout.addLayout(meal_layout)
        add_layout.addWidget(add_btn)
        add_layout.addWidget(self.status_label)
        self.add_tab.setLayout(add_layout)

        # Вкладка "Просмотр"
        view_layout = QVBoxLayout()
        self.date_selector = QDateEdit(self)
        self.date_selector.setCalendarPopup(True)
        self.date_selector.setDate(QDate.currentDate())
        self.date_selector.dateChanged.connect(self.update_meal_list)
        self.meal_list = QListWidget(self)
        nav_layout = QHBoxLayout()
        prev_btn = QPushButton("Предыдущий день")
        prev_btn.clicked.connect(self.prev_day)
        next_btn = QPushButton("Следующий день")
        next_btn.clicked.connect(self.next_day)
        nav_layout.addWidget(prev_btn)
        nav_layout.addWidget(self.date_selector)
        nav_layout.addWidget(next_btn)
        view_layout.addLayout(nav_layout)
        view_layout.addWidget(QLabel("Добавленные продукты:"))
        view_layout.addWidget(self.meal_list)
        self.view_tab.setLayout(view_layout)
        self.update_meal_list()

        # Вкладка "Аналитика"
        analytics_layout = QVBoxLayout()
        self.figure = plt.Figure()
        self.canvas = FigureCanvas(self.figure)
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
        meal_type = self.meal_type.currentText()
        date = self.date_selector.date().toString("yyyy-MM-dd")
        if not food_name:
            self.status_label.setText("Выберите еду из списка!")
            return
        calories, protein, fat, carbs = self.get_nutrition_data(food_name, weight)
        if calories != 0:
            self.db.conn.cursor().execute(
                "INSERT INTO nutrition (user_id, date, meal, meal_type, calories, protein, fat, carbs) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (self.user["id"], date, f"{food_name} {weight}г", meal_type, calories, protein, fat, carbs))
            self.db.conn.commit()
            self.status_label.setText(
                f"Добавлено: {meal_type} - {food_name} {weight}г ({calories:.1f} ккал, {protein:.1f}г белка, {fat:.1f}г жиров, {carbs:.1f}г углеводов)"
            )
            self.update_meal_list()
            self.update_analytics()
            self.check_achievements()

    def get_nutrition_data(self, food_name, weight):
        url = "https://platform.fatsecret.com/rest/server.api"
        food_name_en = self.translator.translate(food_name, src="ru", dest="en").text
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
            food_id = response.json()["foods"]["food"][0]["food_id"]
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

    def update_meal_list(self):
        self.meal_list.clear()
        date = self.date_selector.date().toString("yyyy-MM-dd")
        cursor = self.db.conn.cursor()
        cursor.execute(
            "SELECT meal, meal_type, calories, protein, fat, carbs FROM nutrition WHERE user_id = ? AND date = ?",
            (self.user["id"], date))
        meals = cursor.fetchall()
        for meal in meals:
            meal_str = f"{meal[1]}: {meal[0]} ({meal[2]:.1f} ккал, {meal[3]:.1f}г белка, {meal[4]:.1f}г жиров, {meal[5]:.1f}г углеводов)"
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
        date = self.date_selector.date().toString("yyyy-MM-dd")
        cursor = self.db.conn.cursor()
        cursor.execute(
            "SELECT calories, protein, fat, carbs FROM nutrition WHERE user_id = ? AND date = ?",
            (self.user["id"], date))
        nutrition_data = cursor.fetchall()
        total_calories = sum(row[0] for row in nutrition_data)
        total_protein = sum(row[1] for row in nutrition_data)
        total_fat = sum(row[2] for row in nutrition_data)
        total_carbs = sum(row[3] for row in nutrition_data)

        ax.bar(["Калории", "Белки", "Жиры", "Углеводы"],
               [total_calories, total_protein, total_fat, total_carbs])
        ax.set_title(f"Питание за {date}")
        ax.set_ylabel("Значение")
        self.canvas.draw()

    def check_achievements(self):
        cursor = self.db.conn.cursor()
        week_start = self.date_selector.date().addDays(-6).toString("yyyy-MM-dd")
        week_end = self.date_selector.date().toString("yyyy-MM-dd")
        cursor.execute(
            "SELECT COUNT(*) FROM trainings WHERE user_id = ? AND date BETWEEN ? AND ?",
            (self.user["id"], week_start, week_end))
        training_count = cursor.fetchone()[0]
        if training_count >= 5:
            cursor.execute(
                "SELECT COUNT(*) FROM achievements WHERE user_id = ? AND name = ?",
                (self.user["id"], "5 тренировок за неделю"))
            if cursor.fetchone()[0] == 0:
                self.db.add_achievement(self.user["id"], "5 тренировок за неделю")
                self.status_label.setText("Достижение разблокировано: 5 тренировок за неделю!")

        cursor.execute(
            "SELECT SUM(calories) FROM trainings WHERE user_id = ?",
            (self.user["id"],))
        total_burned = cursor.fetchone()[0] or 0
        if total_burned >= 1000:
            cursor.execute(
                "SELECT COUNT(*) FROM achievements WHERE user_id = ? AND name = ?",
                (self.user["id"], "1000 ккал сожжено"))
            if cursor.fetchone()[0] == 0:
                self.db.add_achievement(self.user["id"], "1000 ккал сожжено")
                self.status_label.setText("Достижение разблокировано: 1000 ккал сожжено!")