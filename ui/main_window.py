from PySide6.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QComboBox, QMessageBox, QSizePolicy
from PySide6.QtCore import QDate, Signal, Qt, QTimer
from PySide6.QtGui import QIcon
from modules.training import TrainingWidget
from modules.nutrition import NutritionWidget
from modules.hydration import HydrationWidget
from modules.calendar import CalendarWidget
from modules.analytics import AnalyticsWidget
from modules.recommendations import RecommendationsWidget
from modules.achievements import AchievementsWidget
from database.db_manager import DatabaseManager

class MainWindow(QMainWindow):
    logout_signal = Signal()  # Сигнал для уведомления о выходе

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = DatabaseManager()
        self.setWindowTitle(f"Sport Tracker - {user['username']}")
        self.setGeometry(100, 100, 800, 600)  # Устанавливаем начальный размер окна
        self.init_ui()

    def init_ui(self):
        # Основной виджет и layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)  # Стандартные отступы

        

        # Создаём контейнер для наложения QTabWidget и кнопки "Выйти"
        self.overlay_widget = QWidget()
        overlay_layout = QVBoxLayout(self.overlay_widget)
        overlay_layout.setContentsMargins(0, 0, 0, 0)

        # Вкладки
        self.tabs = QTabWidget()
        self.tabs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Растягиваем по ширине и высоте

        # Применяем стиль для вкладок
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #00C8FF;
                border-radius: 5px;
                background-color: #1A1A22;  /* Указываем цвет фона явно */
                margin-top: 20px;  /* Отступ сверху */
                margin-bottom: 10px;  /* Отступ снизу */
                margin-left: 5px;  /* Отступ слева */
                margin-right: 5px;  /* Стандартный правый отступ */
            }
            QTabBar::tab {
                background: #1C2526;
                color: #DCDCDC;
                padding: 8px 20px;
                margin-right: 5px;
                border: 1px solid #00C8FF;
                border-radius: 5px;
            }
            QTabBar::tab:selected {
                background: #00C8FF;
                color: #1C2526;
            }
            QTabBar::tab:hover {
                background: #4A6A6D;
            }
        """)

        # Кнопка выхода
        self.logout_btn = QPushButton("Выйти")
        self.logout_btn.setAccessibleName("action")
        self.logout_btn.setIcon(QIcon("icons/logout.png"))
        self.logout_btn.clicked.connect(self.logout)

        # Устанавливаем размер кнопки "Выйти" с той же высотой, что у вкладок
        tab_bar_height = self.tabs.tabBar().height()  # Измеряем высоту QTabBar
        self.logout_btn.setFixedSize(80, tab_bar_height)  # Увеличиваем ширину до 80, высота как у вкладок
        self.logout_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Добавляем QTabWidget в overlay_layout
        overlay_layout.addWidget(self.tabs)

        # Добавляем overlay_widget в main_layout
        main_layout.addWidget(self.overlay_widget)

        # Налагаем кнопку "Выйти" поверх QTabWidget
        self.logout_btn.setParent(self.overlay_widget)  # Устанавливаем родителя

        # Функция для обновления позиции кнопки
        def update_logout_btn_position():
            tab_bar_height = self.tabs.tabBar().height()
            # Используем ширину overlay_widget, но проверяем, что она не 0
            widget_width = self.overlay_widget.width()
            if widget_width <= 0:  # Если ширина некорректна, используем ширину окна
                widget_width = self.width() - main_layout.contentsMargins().left() - main_layout.contentsMargins().right()
            if widget_width <= 0:  # Если и ширина окна некорректна, используем начальную ширину из setGeometry
                widget_width = 800  # Начальная ширина из setGeometry(100, 100, 800, 600)
            self.logout_btn.move(widget_width - self.logout_btn.width() - 10, (tab_bar_height - self.logout_btn.height()) // 2)

        # Сохраняем функцию как атрибут, чтобы использовать её в других методах
        self.update_logout_btn_position = update_logout_btn_position

        # Обновляем позицию кнопки при переключении вкладок
        self.tabs.currentChanged.connect(self.update_logout_btn_position)

        # Создаём виджеты для вкладок
        self.profile_widget = QWidget()
        self.training_widget = TrainingWidget(self.user)
        self.nutrition_widget = NutritionWidget(self.user)
        self.hydration_widget = HydrationWidget(self.user)
        self.calendar_widget = CalendarWidget(self.user)
        self.analytics_widget = AnalyticsWidget(self.user)
        self.recommendations_widget = RecommendationsWidget(self.user)
        self.achievements_widget = AchievementsWidget(self.user)

        # Подключаем сигналы для синхронизации между CalendarWidget и TrainingWidget
        self.calendar_widget.data_saved.connect(self.training_widget.apply_planned_training)
        self.training_widget.training_added.connect(self.calendar_widget.load_day_data)

        # Вкладка "Профиль"
        profile_inner_layout = QVBoxLayout()
        profile_inner_layout.setSpacing(10)
        profile_inner_layout.setAlignment(Qt.AlignTop)  # Выравниваем элементы по верхнему краю

        title_label = QLabel("Профиль пользователя")
        title_label.setAccessibleName("header")

        self.weight_input = QLineEdit()
        self.weight_input.setPlaceholderText("Вес (кг)")
        self.weight_input.setMinimumWidth(300)  # Увеличиваем минимальную ширину
        self.weight_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Растягиваем по ширине

        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("Рост (см)")
        self.height_input.setMinimumWidth(300)
        self.height_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.age_input = QLineEdit()
        self.age_input.setPlaceholderText("Возраст")
        self.height_input.setMinimumWidth(300)
        self.age_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.gender_input = QComboBox()
        self.gender_input.addItems(["М", "Ж"])
        self.gender_input.setMinimumWidth(300)
        self.gender_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        save_profile_btn = QPushButton("Сохранить профиль")
        save_profile_btn.setAccessibleName("action")
        save_profile_btn.setIcon(QIcon("icons/save.png"))
        save_profile_btn.clicked.connect(self.save_profile)
        save_profile_btn.setMinimumWidth(150)
        save_profile_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.profile_status_label = QLabel("Введите данные профиля")
        self.profile_status_label.setAccessibleName("small")

        save_profile_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9500;
                color: #FFFFFF;
                border-radius: 8px;
                padding: 7px 10px;
            }
            QPushButton:hover {
                background-color: #E68A00;
            }
            QPushButton:pressed {
                background-color: #CC7700;
            }
        """)

        # Создаем QHBoxLayout для центрирования кнопки
        save_profile_layout = QHBoxLayout()
        save_profile_layout.addStretch()  # Растяжка слева
        save_profile_layout.addWidget(save_profile_btn)  # Добавляем кнопку
        save_profile_layout.addStretch()  # Растяжка справа

        profile_inner_layout.addWidget(title_label)
        profile_inner_layout.addWidget(QLabel("Вес (кг):"))
        profile_inner_layout.addWidget(self.weight_input)
        profile_inner_layout.addWidget(QLabel("Рост (см):"))
        profile_inner_layout.addWidget(self.height_input)
        profile_inner_layout.addWidget(QLabel("Возраст:"))
        profile_inner_layout.addWidget(self.age_input)
        profile_inner_layout.addWidget(QLabel("Пол:"))
        profile_inner_layout.addWidget(self.gender_input)
        profile_inner_layout.addLayout(save_profile_layout)
        profile_inner_layout.addWidget(self.profile_status_label)
        profile_inner_layout.addStretch()

        # Создаём центрирующий layout для profile_widget
        profile_layout = QHBoxLayout()
        profile_layout.setAlignment(Qt.AlignCenter)
        profile_inner_widget = QWidget()
        profile_inner_widget.setLayout(profile_inner_layout)
        profile_layout.addWidget(profile_inner_widget)
        self.profile_widget.setLayout(profile_layout)

        # Список вкладок для добавления
        tab_widgets = [
            (self.profile_widget, "Профиль", "icons/profile.png"),
            (self.training_widget, "Тренировки", "icons/trainings.PNG"),
            (self.nutrition_widget, "Питание", "icons/nutrition.PNG"),
            (self.hydration_widget, "Вода", "icons/water.PNG"),
            (self.calendar_widget, "Календарь", "icons/calendar.PNG"),
            
            (self.recommendations_widget, "Рекомендации", "icons/recommendations.PNG"),
            (self.achievements_widget, "Достижения", "icons/achievements.PNG"),
        ]

        # Добавляем вкладки с иконками
        for widget, title, icon_path in tab_widgets:
            if widget.layout() is None:
                temp_layout = QVBoxLayout()
                temp_layout.setAlignment(Qt.AlignTop)
                widget.setLayout(temp_layout)
            self.tabs.addTab(widget, QIcon(icon_path), title)

        # Загружаем профиль
        self.load_profile()

        # Подключаем сигналы для синхронизации RecommendationsWidget
        self.calendar_widget.data_saved.connect(self.recommendations_widget.update_recommendations)
        self.training_widget.training_added.connect(self.recommendations_widget.update_recommendations)
        # Проверяем, есть ли сигнал data_updated в NutritionWidget и HydrationWidget
        try:
            self.nutrition_widget.data_updated.connect(self.recommendations_widget.update_recommendations)
        except AttributeError:
            pass  # Если сигнала нет, пропускаем
        try:
            self.hydration_widget.data_updated.connect(self.recommendations_widget.update_recommendations)
        except AttributeError:
            pass  # Если сигнала нет, пропускаем

        # Синхронизация достижений (если есть такие методы в виджетах)
        try:
            self.training_widget.training_list.itemChanged.connect(self.achievements_widget.update_achievements)
            self.nutrition_widget.meal_list.itemChanged.connect(self.achievements_widget.update_achievements)
        except AttributeError:
            pass  # Если методы отсутствуют, просто пропускаем

        # Проверка напоминаний
        self.check_reminders()

        # Открываем окно в оконном режиме
        self.show()

    def showEvent(self, event):
        super().showEvent(event)
        # Принудительно пересчитываем размеры всех виджетов
        self.overlay_widget.updateGeometry()
        self.adjustSize()
        # Обновляем позицию кнопки с небольшой задержкой, чтобы дать Qt время на пересчёт размеров
        QTimer.singleShot(0, self._update_logout_btn_with_check)

    def _update_logout_btn_with_check(self):
        self.logout_btn.raise_()  # Поднимаем кнопку на передний план
        self.update_logout_btn_position()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_logout_btn_position()

    def save_profile(self):
        try:
            weight_text = self.weight_input.text().strip() or "0"
            height_text = self.height_input.text().strip() or "0"
            age_text = self.age_input.text().strip() or "0"
            gender = self.gender_input.currentText()

            weight = float(weight_text)
            height = float(height_text)
            age = int(age_text)

            if weight <= 0 or height <= 0 or age <= 0:
                raise ValueError("Все значения должны быть больше 0")

            self.db.update_user_profile(self.user["id"], weight, height, age, gender)
            self.profile_status_label.setText("Профиль сохранён")
            QMessageBox.information(self, "Успех", "Профиль успешно сохранён!")
        except ValueError as e:
            error_message = "Ошибка: введите корректные числовые значения (вес, рост, возраст)"
            if "больше 0" in str(e):
                error_message = "Ошибка: все значения должны быть больше 0"
            self.profile_status_label.setText(error_message)
            QMessageBox.warning(self, "Ошибка", error_message)

    def load_profile(self):
        profile = self.db.get_user_profile(self.user["id"])
        if profile and all(profile):
            self.weight_input.setText(str(profile[0]))
            self.height_input.setText(str(profile[1]))
            self.age_input.setText(str(profile[2]))
            self.gender_input.setCurrentText(profile[3])
            self.profile_status_label.setText("Профиль загружен")
        else:
            self.weight_input.setText("")
            self.height_input.setText("")
            self.age_input.setText("")
            self.gender_input.setCurrentText("М")
            self.profile_status_label.setText("Профиль не заполнен, введите данные")

    def check_reminders(self):
        cursor = self.db.conn.cursor()
        today = QDate.currentDate().toString("yyyy-MM-dd")
        cursor.execute(
            "SELECT training_type, training_duration FROM calendar WHERE user_id = ? AND date = ? AND completed = 0",
            (self.user["id"], today))
        reminders = cursor.fetchall()
        for reminder in reminders:
            if reminder[0]:
                msg = QMessageBox(self)
                msg.setWindowTitle("Напоминание")
                msg.setText(f"Сегодня: {reminder[0]} ({reminder[1]} мин)")
                msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Ignore)
                msg.setDefaultButton(QMessageBox.Ok)
                msg.button(QMessageBox.Ok).setText("Перейти к тренировке")
                msg.button(QMessageBox.Ignore).setText("Пропустить")
                reply = msg.exec_()
                if reply == QMessageBox.Ok:
                    self.tabs.setCurrentWidget(self.training_widget)
                    self.training_widget.date_selector.setDate(QDate.currentDate())

    def logout(self):
        self.logout_signal.emit()
        self.close()

    def closeEvent(self, event):
        self.db.conn.close()
        event.accept()