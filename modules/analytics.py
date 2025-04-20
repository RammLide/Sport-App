# analytics.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QLabel, QHBoxLayout, QSizePolicy
from PySide6.QtCore import QDate, Qt
from database.db_manager import DatabaseManager
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class AnalyticsWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = DatabaseManager()
        self.init_ui()

    def init_ui(self):
        # Основной layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)

        # Внутренний контейнер для центрирования
        inner_widget = QWidget()
        inner_layout = QVBoxLayout(inner_widget)
        inner_layout.setSpacing(15)

        # Заголовок
        title_label = QLabel("Аналитика активности")
        title_label.setAccessibleName("header")
        inner_layout.addWidget(title_label)

        # Выбор периода
        period_layout = QHBoxLayout()
        period_label = QLabel("Период:")
        period_label.setAccessibleName("small")
        self.period_selector = QComboBox()
        self.period_selector.addItems(["Неделя", "Месяц", "Год"])
        self.period_selector.currentTextChanged.connect(self.update_analytics)
        period_layout.addWidget(period_label)
        period_layout.addWidget(self.period_selector)
        period_layout.addStretch()
        inner_layout.addLayout(period_layout)

        # График
        # Увеличиваем размер фигуры и делаем ширину адаптивной
        self.figure = plt.Figure(figsize=(12, 8))  # Увеличиваем базовую ширину
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Растягиваем
        inner_layout.addWidget(self.canvas)

        # Статистика
        self.stats_label = QLabel("Статистика:")
        self.stats_label.setAccessibleName("header")
        inner_layout.addWidget(self.stats_label)

        # Центрируем содержимое
        main_layout.addWidget(inner_widget, alignment=Qt.AlignCenter)
        main_layout.addStretch()

        self.setLayout(main_layout)
        self.update_analytics()

    def update_analytics(self):
        self.figure.clear()
        period = self.period_selector.currentText()
        end_date = QDate.currentDate()
        if period == "Неделя":
            start_date = end_date.addDays(-6)
        elif period == "Месяц":
            start_date = end_date.addMonths(-1)
        else:  # Год
            start_date = end_date.addYears(-1)

        start_date_str = start_date.toString("yyyy-MM-dd")
        end_date_str = end_date.toString("yyyy-MM-dd")

        cursor = self.db.conn.cursor()

        # Аналитика тренировок
        cursor.execute(
            """
            SELECT date, duration, calories
            FROM trainings
            WHERE user_id = ? AND date BETWEEN ? AND ?
            ORDER BY date
            """,
            (self.user["id"], start_date_str, end_date_str)
        )
        training_data = cursor.fetchall()

        # Аналитика питания
        cursor.execute(
            """
            SELECT date, SUM(calories), SUM(protein), SUM(fat), SUM(carbs)
            FROM nutrition
            WHERE user_id = ? AND date BETWEEN ? AND ?
            GROUP BY date
            """,
            (self.user["id"], start_date_str, end_date_str)
        )
        nutrition_data = cursor.fetchall()

        # Аналитика воды
        cursor.execute(
            """
            SELECT date, SUM(amount)
            FROM hydration
            WHERE user_id = ? AND date BETWEEN ? AND ?
            GROUP BY date
            """,
            (self.user["id"], start_date_str, end_date_str)
        )
        hydration_data = cursor.fetchall()

        # График
        ax1 = self.figure.add_subplot(311)  # Тренировки
        ax2 = self.figure.add_subplot(312)  # Питание
        ax3 = self.figure.add_subplot(313)  # Вода

        # Тренировки
        if training_data:
            dates = [row[0][-5:] for row in training_data]
            durations = [row[1] for row in training_data]
            calories = [row[2] for row in training_data]
            ax1.bar(dates, durations, width=0.4, label="Длительность (мин)", color="#00C8FF")
            ax1.bar([i + 0.4 for i in range(len(dates))], calories, width=0.4, label="Калории (ккал)", color="#FF6347")
            ax1.legend(fontsize=6)  # Уменьшаем шрифт легенды
            ax1.set_xticks(range(len(dates)))
            ax1.set_xticklabels(dates, rotation=45, fontsize=6)  # Уменьшаем шрифт подписей
            for i, v in enumerate(durations):
                ax1.text(i, v + 1, str(v), ha='center', fontsize=6)  # Уменьшаем шрифт текста
            for i, v in enumerate(calories):
                ax1.text(i + 0.4, v + 1, f"{v:.1f}", ha='center', fontsize=6)
            ax1.set_title(f"Тренировки ({period.lower()})", fontsize=8)  # Уменьшаем шрифт заголовка
            ax1.set_xlabel("Дата", fontsize=6)
            ax1.set_ylabel("Значение", fontsize=6)

        # Питание
        if nutrition_data:
            dates = [row[0][-5:] for row in nutrition_data]
            calories = [row[1] for row in nutrition_data]
            protein = [row[2] for row in nutrition_data]
            fat = [row[3] for row in nutrition_data]
            carbs = [row[4] for row in nutrition_data]
            ax2.plot(dates, calories, label="Калории (ккал)", color="#FF6347")
            ax2.plot(dates, protein, label="Белки (г)", color="#00C8FF")
            ax2.plot(dates, fat, label="Жиры (г)", color="#FFD700")
            ax2.plot(dates, carbs, label="Углеводы (г)", color="#32CD32")
            ax2.legend(fontsize=6)
            ax2.set_xticks(range(len(dates)))
            ax2.set_xticklabels(dates, rotation=45, fontsize=6)
            ax2.set_title(f"Питание ({period.lower()})", fontsize=8)
            ax2.set_xlabel("Дата", fontsize=6)
            ax2.set_ylabel("Значение", fontsize=6)

        # Вода
        if hydration_data:
            dates = [row[0][-5:] for row in hydration_data]
            amounts = [row[1] for row in hydration_data]
            ax3.bar(dates, amounts, color="#00C8FF")
            ax3.set_title(f"Вода ({period.lower()})", fontsize=8)
            ax3.set_xlabel("Дата", fontsize=6)
            ax3.set_ylabel("Объем (мл)", fontsize=6)
            ax3.set_xticks(range(len(dates)))
            ax3.set_xticklabels(dates, rotation=45, fontsize=6)
            for i, v in enumerate(amounts):
                ax3.text(i, v + max(amounts)*0.01, f"{v:.0f}", ha='center', fontsize=6)
        else:
            ax3.text(0.5, 0.5, "Нет данных о воде", ha='center', va='center', fontsize=8)

        # Статистика
        stats_text = "Статистика тренировок:\n"
        cursor.execute(
            """
            SELECT tt.name, SUM(t.duration), SUM(t.calories)
            FROM trainings t
            JOIN training_types tt ON t.type_id = tt.id
            WHERE t.user_id = ? AND t.date BETWEEN ? AND ?
            GROUP BY tt.name
            """,
            (self.user["id"], start_date_str, end_date_str)
        )
        training_stats = cursor.fetchall()
        total_duration = 0
        total_calories = 0
        for stat in training_stats:
            stats_text += f"{stat[0]}: {stat[1]} мин, {stat[2]:.1f} ккал\n"
            total_duration += stat[1] or 0
            total_calories += stat[2] or 0
        stats_text += f"Итого: {total_duration} мин, {total_calories:.1f} ккал\n\n"

        stats_text += "Статистика питания:\n"
        cursor.execute(
            """
            SELECT SUM(calories), SUM(protein), SUM(fat), SUM(carbs)
            FROM nutrition
            WHERE user_id = ? AND date BETWEEN ? AND ?
            """,
            (self.user["id"], start_date_str, end_date_str)
        )
        nutrition_stats = cursor.fetchone()
        if nutrition_stats and nutrition_stats[0]:
            stats_text += f"Калории: {nutrition_stats[0]:.1f} ккал\n"
            stats_text += f"Белки: {nutrition_stats[1]:.1f} г\n"
            stats_text += f"Жиры: {nutrition_stats[2]:.1f} г\n"
            stats_text += f"Углеводы: {nutrition_stats[3]:.1f} г\n"
        else:
            stats_text += "Нет данных о питании\n"

        stats_text += "\nСтатистика воды:\n"
        total_water = self.db.get_hydration_stats(self.user["id"], start_date_str, end_date_str)
        stats_text += f"Всего: {total_water:.0f} мл\n"
        profile = self.db.get_user_profile(self.user["id"])
        if profile and profile[0]:
            recommended = profile[0] * 30 * 7  # 30 мл/кг в день за неделю
            stats_text += f"Рекомендуемая норма (неделя): {recommended:.0f} мл"

        self.stats_label.setText(stats_text)
        self.figure.tight_layout(pad=3.0)  # Увеличиваем отступы
        self.canvas.draw()