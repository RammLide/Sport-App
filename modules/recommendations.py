from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import QDate, Signal
from database.db_manager import DatabaseManager

class RecommendationsWidget(QWidget):
    data_updated = Signal()  # Сигнал для уведомления об обновлении данных

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = DatabaseManager()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Заголовок
        title_label = QLabel("Рекомендации для вас")
        title_label.setAccessibleName("header")
        layout.addWidget(title_label)

        # Метки для рекомендаций (без иконок)
        self.calories_label = QLabel()
        self.training_label = QLabel()
        self.hydration_label = QLabel()

        # Стилизация меток
        label_style = """
            QLabel {
                font-size: 12px;
                font-weight: normal;
                color: #FFFFFF;
                background-color: #2A2A3A;
                padding: 2px;
                min-height: 20px;
            }
        """
        self.calories_label.setStyleSheet(label_style)
        self.training_label.setStyleSheet(label_style)
        self.hydration_label.setStyleSheet(label_style)

        # Добавляем метки напрямую в layout
        layout.addWidget(self.calories_label)
        layout.addWidget(self.training_label)
        layout.addWidget(self.hydration_label)

        layout.setSpacing(2)
        self.setLayout(layout)
        self.update_recommendations()

    def update_recommendations(self):
        date = QDate.currentDate().toString("yyyy-MM-dd")
        cursor = self.db.conn.cursor()

        # Получаем данные профиля пользователя
        profile = self.db.get_user_profile(self.user["id"])
        daily_calories_norm = 2000  # Значение по умолчанию
        if profile and all(profile):
            weight, height, age, gender = profile
            # Формула Миффлина-Сан Жеора
            if gender == "М":
                daily_calories_norm = 10 * weight + 6.25 * height - 5 * age + 5
            else:
                daily_calories_norm = 10 * weight + 6.25 * height - 5 * age - 161
            daily_calories_norm *= 1.5  # Учитываем среднюю активность

        # Получаем данные о питании
        cursor.execute(
            "SELECT calories FROM nutrition WHERE user_id = ? AND date = ?",
            (self.user["id"], date))
        nutrition_data = cursor.fetchall()
        total_calories = sum(row[0] for row in nutrition_data)

        # Получаем данные о тренировках
        cursor.execute(
            "SELECT calories, duration, type_id FROM trainings WHERE user_id = ? AND date = ?",
            (self.user["id"], date))
        training_data = cursor.fetchall()
        total_burned = sum(row[0] for row in training_data)
        total_duration = sum(row[1] for row in training_data)
        training_types = [row[2] for row in training_data]

        # Получаем данные о гидратации
        cursor.execute(
            "SELECT hydration_amount FROM calendar WHERE user_id = ? AND date = ?",
            (self.user["id"], date))
        hydration_data = cursor.fetchone()
        total_water = hydration_data[0] if hydration_data and hydration_data[0] is not None else 0

        # Получаем статистику тренировок за последние 7 дней для рекомендаций по тренировкам
        start_date = QDate.currentDate().addDays(-7).toString("yyyy-MM-dd")
        cursor.execute(
            """
            SELECT tt.name, SUM(t.duration)
            FROM trainings t
            JOIN training_types tt ON t.type_id = tt.id
            WHERE t.user_id = ? AND t.date BETWEEN ? AND ?
            GROUP BY tt.name
            """,
            (self.user["id"], start_date, date))
        training_stats = cursor.fetchall()
        training_dict = dict(training_stats)

        # Рекомендации по калориям
        balance = total_calories - total_burned
        calories_advice = ""
        if not total_calories and not total_burned:
            calories_advice = "Добавьте данные о питании и тренировках для анализа."
        elif balance > daily_calories_norm * 0.2:
            calories_advice = f"Вы превышаете норму на {int(balance - daily_calories_norm)} ккал. Сократите потребление или увеличьте тренировки."
        elif balance < daily_calories_norm * 0.8:
            calories_advice = f"Вы недобираете {int(daily_calories_norm - balance)} ккал. Добавьте больше калорий в рацион."
        else:
            calories_advice = "Хороший баланс калорий! Продолжайте в том же духе."

        self.calories_label.setText(f"Калории: {calories_advice}")

        # Рекомендации по тренировкам
        training_advice = ""
        if not training_data:
            training_advice = "Сегодня нет тренировок. Попробуйте добавить лёгкую тренировку, например, бег или йогу."
        elif total_duration < 30:
            training_advice = "Тренировки слишком короткие. Постарайтесь заниматься хотя бы 30 минут."
        else:
            recommended_type = "Йога" if "Йога" not in training_dict else "Силовая" if "Силовая" not in training_dict else "Бег"
            training_advice = f"Отличная работа! Попробуйте разнообразить тренировки, добавив {recommended_type.lower()}."

        self.training_label.setText(f"Тренировки: {training_advice}")

        # Рекомендации по гидратации
        hydration_advice = ""
        daily_water_norm = 2.0  # 2 литра в день
        if profile and profile[0]:  # Если есть вес
            daily_water_norm = profile[0] * 0.03  # 30 мл на 1 кг веса
        if total_water == 0:
            hydration_advice = "Не забыли ли вы пить воду? Добавьте данные о гидратации."
        elif total_water < daily_water_norm:
            hydration_advice = f"Вы выпили {total_water} л. Это меньше нормы ({daily_water_norm:.1f} л). Выпейте ещё {daily_water_norm - total_water:.1f} л."
        else:
            hydration_advice = f"Отлично! Вы выпили {total_water} л, это соответствует норме ({daily_water_norm:.1f} л)."

        self.hydration_label.setText(f"Гидратация: {hydration_advice}")