from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QHBoxLayout, QComboBox, QListWidget, QDateEdit, QTabWidget, QMessageBox, QFormLayout, QListWidgetItem
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QColor
from database.db_manager import DatabaseManager
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class TrainingWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = DatabaseManager()
        self.exercises = []  # Список для временного хранения упражнений
        self.cardio_types = ["Бег", "Велосипед", "Плавание", "Ходьба"]
        self.editing_training_id = None  # ID тренировки для редактирования
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.add_tab = QWidget()
        self.view_tab = QWidget()
        self.edit_tab = QWidget()
        self.analytics_tab = QWidget()
        self.tabs.addTab(self.add_tab, "Добавить тренировку")
        self.tabs.addTab(self.view_tab, "Просмотр")
        self.tabs.addTab(self.edit_tab, "Редактировать тренировку")
        self.tabs.addTab(self.analytics_tab, "Аналитика")
        layout.addWidget(self.tabs)

        # Вкладка "Добавить тренировку"
        add_layout = QVBoxLayout()
        title_label = QLabel("Добавить тренировку")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #00C8FF;")

        self.template_selector = QComboBox(self)
        self.populate_templates()
        self.template_selector.currentTextChanged.connect(self.apply_template)

        training_layout = QHBoxLayout()
        self.type_input = QComboBox(self)
        training_types = self.db.get_training_types()
        self.type_input.addItems([t[1] for t in training_types])
        self.type_input.currentTextChanged.connect(self.update_exercise_form)
        self.duration_input = QLineEdit(self)
        self.duration_input.setPlaceholderText("Длительность (мин)")
        training_layout.addWidget(self.type_input)
        training_layout.addWidget(self.duration_input)

        self.exercise_form = QFormLayout()
        self.exercise_name = QComboBox(self)
        self.exercise_name.setEditable(True)
        self.exercise_name.addItems([e[1] for e in self.db.get_exercises_by_type(1)])  # Начально Силовая
        self.sets_input = QLineEdit(self)
        self.sets_input.setPlaceholderText("Подходы")
        self.reps_input = QLineEdit(self)
        self.reps_input.setPlaceholderText("Повторения")
        self.weight_input = QLineEdit(self)
        self.weight_input.setPlaceholderText("Вес (кг)")
        self.distance_input = QLineEdit(self)
        self.distance_input.setPlaceholderText("Дистанция (км)")
        self.pace_input = QLineEdit(self)
        self.pace_input.setPlaceholderText("Темп (мин/км)")

        self.exercise_form.addRow("Упражнение:", self.exercise_name)
        self.exercise_form.addRow("Подходы:", self.sets_input)
        self.exercise_form.addRow("Повторения:", self.reps_input)
        self.exercise_form.addRow("Вес (кг):", self.weight_input)
        self.exercise_form.addRow("Дистанция (км):", self.distance_input)
        self.exercise_form.addRow("Темп (мин/км):", self.pace_input)

        add_exercise_btn = QPushButton("Добавить упражнение в список")
        add_exercise_btn.clicked.connect(self.add_exercise_to_list)
        clear_exercises_btn = QPushButton("Очистить список упражнений")
        clear_exercises_btn.clicked.connect(self.clear_exercise_list)
        self.exercise_list_label = QLabel("Добавленные упражнения: 0")

        save_template_btn = QPushButton("Сохранить как шаблон")
        save_template_btn.clicked.connect(self.save_template)
        self.template_name_input = QLineEdit(self)
        self.template_name_input.setPlaceholderText("Название шаблона")

        add_btn = QPushButton("Сохранить тренировку")
        add_btn.clicked.connect(self.add_training)
        repeat_btn = QPushButton("Повторить последнюю")
        repeat_btn.clicked.connect(self.repeat_last_training)
        self.status_label = QLabel("Введите данные тренировки")

        add_layout.addWidget(title_label)
        add_layout.addWidget(QLabel("Выбрать шаблон:"))
        add_layout.addWidget(self.template_selector)
        add_layout.addLayout(training_layout)
        add_layout.addWidget(QLabel("Добавить упражнение:"))
        add_layout.addLayout(self.exercise_form)
        add_layout.addWidget(add_exercise_btn)
        add_layout.addWidget(clear_exercises_btn)
        add_layout.addWidget(self.exercise_list_label)
        add_layout.addWidget(QLabel("Название шаблона:"))
        add_layout.addWidget(self.template_name_input)
        add_layout.addWidget(save_template_btn)
        add_layout.addWidget(add_btn)
        add_layout.addWidget(repeat_btn)
        add_layout.addWidget(self.status_label)
        self.add_tab.setLayout(add_layout)

        # Вкладка "Редактировать тренировку"
        edit_layout = QVBoxLayout()
        edit_title_label = QLabel("Редактировать тренировку")
        edit_title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #00C8FF;")

        self.edit_type_input = QComboBox(self)
        self.edit_type_input.addItems([t[1] for t in training_types])
        self.edit_type_input.currentTextChanged.connect(self.update_edit_exercise_form)
        self.edit_duration_input = QLineEdit(self)
        self.edit_duration_input.setPlaceholderText("Длительность (мин)")

        self.edit_exercise_form = QFormLayout()
        self.edit_exercise_name = QComboBox(self)
        self.edit_exercise_name.setEditable(True)
        self.edit_exercise_name.addItems([e[1] for e in self.db.get_exercises_by_type(1)])
        self.edit_sets_input = QLineEdit(self)
        self.edit_sets_input.setPlaceholderText("Подходы")
        self.edit_reps_input = QLineEdit(self)
        self.edit_reps_input.setPlaceholderText("Повторения")
        self.edit_weight_input = QLineEdit(self)
        self.edit_weight_input.setPlaceholderText("Вес (кг)")
        self.edit_distance_input = QLineEdit(self)
        self.edit_distance_input.setPlaceholderText("Дистанция (км)")
        self.edit_pace_input = QLineEdit(self)
        self.edit_pace_input.setPlaceholderText("Темп (мин/км)")

        self.edit_exercise_form.addRow("Упражнение:", self.edit_exercise_name)
        self.edit_exercise_form.addRow("Подходы:", self.edit_sets_input)
        self.edit_exercise_form.addRow("Повторения:", self.edit_reps_input)
        self.edit_exercise_form.addRow("Вес (кг):", self.edit_weight_input)
        self.edit_exercise_form.addRow("Дистанция (км):", self.edit_distance_input)
        self.edit_exercise_form.addRow("Темп (мин/км):", self.edit_pace_input)

        edit_add_exercise_btn = QPushButton("Добавить упражнение в список")
        edit_add_exercise_btn.clicked.connect(self.add_edit_exercise_to_list)
        edit_clear_exercises_btn = QPushButton("Очистить список упражнений")
        edit_clear_exercises_btn.clicked.connect(self.clear_edit_exercise_list)
        self.edit_exercise_list_label = QLabel("Добавленные упражнения: 0")

        save_edit_btn = QPushButton("Сохранить изменения")
        save_edit_btn.clicked.connect(self.save_edited_training)
        self.edit_status_label = QLabel("Выберите тренировку для редактирования")

        edit_layout.addWidget(edit_title_label)
        edit_layout.addWidget(QLabel("Тип тренировки:"))
        edit_layout.addWidget(self.edit_type_input)
        edit_layout.addWidget(QLabel("Длительность:"))
        edit_layout.addWidget(self.edit_duration_input)
        edit_layout.addWidget(QLabel("Добавить упражнение:"))
        edit_layout.addLayout(self.edit_exercise_form)
        edit_layout.addWidget(edit_add_exercise_btn)
        edit_layout.addWidget(edit_clear_exercises_btn)
        edit_layout.addWidget(self.edit_exercise_list_label)
        edit_layout.addWidget(save_edit_btn)
        edit_layout.addWidget(self.edit_status_label)
        self.edit_tab.setLayout(edit_layout)

        # Вкладка "Просмотр"
        view_layout = QVBoxLayout()
        self.date_selector = QDateEdit(self)
        self.date_selector.setCalendarPopup(True)
        self.date_selector.setDate(QDate.currentDate())
        self.date_selector.dateChanged.connect(self.update_training_list)
        self.training_list = QListWidget(self)
        self.training_list.itemClicked.connect(self.enable_edit_delete_buttons)
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
        self.edit_btn.clicked.connect(self.edit_training)
        self.edit_btn.setEnabled(False)
        self.delete_btn = QPushButton("Удалить")
        self.delete_btn.clicked.connect(self.delete_training)
        self.delete_btn.setEnabled(False)
        action_layout.addWidget(self.edit_btn)
        action_layout.addWidget(self.delete_btn)

        view_layout.addLayout(nav_layout)
        view_layout.addWidget(QLabel("Добавленные тренировки:"))
        view_layout.addWidget(self.training_list)
        view_layout.addLayout(action_layout)
        self.view_tab.setLayout(view_layout)
        self.update_training_list()

        # Вкладка "Аналитика"
        analytics_layout = QVBoxLayout()
        self.figure = plt.Figure()
        self.canvas = FigureCanvas(self.figure)
        self.stats_label = QLabel("Статистика по типам тренировок:")
        analytics_layout.addWidget(self.stats_label)
        analytics_layout.addWidget(self.canvas)
        self.analytics_tab.setLayout(analytics_layout)
        self.update_analytics()

        self.setLayout(layout)
        self.update_exercise_form()
        self.update_edit_exercise_form()

    def update_exercise_form(self):
        training_type = self.type_input.currentText()
        is_cardio = training_type in self.cardio_types
        type_id = next((t[0] for t in self.db.get_training_types() if t[1] == training_type), 1)
        self.exercise_name.clear()
        exercises = sorted([e[1] for e in self.db.get_exercises_by_type(type_id)])  # Сортировка
        self.exercise_name.addItems(exercises)
        self.sets_input.setVisible(not is_cardio)
        self.reps_input.setVisible(not is_cardio)
        self.weight_input.setVisible(not is_cardio)
        self.distance_input.setVisible(is_cardio)
        self.pace_input.setVisible(is_cardio)
        for i in range(self.exercise_form.rowCount()):
            label_item = self.exercise_form.itemAt(i, QFormLayout.LabelRole)
            field_item = self.exercise_form.itemAt(i, QFormLayout.FieldRole)
            if field_item and field_item.widget():
                label_item.widget().setVisible(field_item.widget().isVisible())

    def update_edit_exercise_form(self):
        training_type = self.edit_type_input.currentText()
        is_cardio = training_type in self.cardio_types
        type_id = next((t[0] for t in self.db.get_training_types() if t[1] == training_type), 1)
        self.edit_exercise_name.clear()
        self.edit_exercise_name.addItems([e[1] for e in self.db.get_exercises_by_type(type_id)])
        self.edit_sets_input.setVisible(not is_cardio)
        self.edit_reps_input.setVisible(not is_cardio)
        self.edit_weight_input.setVisible(not is_cardio)
        self.edit_distance_input.setVisible(is_cardio)
        self.edit_pace_input.setVisible(is_cardio)
        for i in range(self.edit_exercise_form.rowCount()):
            label_item = self.edit_exercise_form.itemAt(i, QFormLayout.LabelRole)
            field_item = self.edit_exercise_form.itemAt(i, QFormLayout.FieldRole)
            if field_item and field_item.widget():
                label_item.widget().setVisible(field_item.widget().isVisible())

    def add_exercise_to_list(self):
        exercise_name = self.exercise_name.currentText()
        if not exercise_name:
            self.status_label.setText("Выберите или введите упражнение")
            return
        exercise = {
            "name": exercise_name,
            "sets": self.sets_input.text() or "0",
            "reps": self.reps_input.text() or "0",
            "weight": self.weight_input.text() or "0",
            "distance": self.distance_input.text() or "0",
            "pace": self.pace_input.text() or "0"
        }
        try:
            exercise["sets"] = int(exercise["sets"])
            exercise["reps"] = int(exercise["reps"])
            exercise["weight"] = float(exercise["weight"])
            exercise["distance"] = float(exercise["distance"])
            exercise["pace"] = float(exercise["pace"])
            self.exercises.append(exercise)
            self.exercise_list_label.setText(f"Добавленные упражнения: {len(self.exercises)}")
            self.exercise_name.setCurrentIndex(-1)
            self.sets_input.clear()
            self.reps_input.clear()
            self.weight_input.clear()
            self.distance_input.clear()
            self.pace_input.clear()
            self.status_label.setText(f"Добавлено упражнение: {exercise_name}")
        except ValueError:
            self.status_label.setText("Ошибка: введите корректные числа")

    def add_edit_exercise_to_list(self):
        exercise_name = self.edit_exercise_name.currentText()
        if not exercise_name:
            self.edit_status_label.setText("Выберите или введите упражнение")
            return
        exercise = {
            "name": exercise_name,
            "sets": self.edit_sets_input.text() or "0",
            "reps": self.edit_reps_input.text() or "0",
            "weight": self.edit_weight_input.text() or "0",
            "distance": self.edit_distance_input.text() or "0",
            "pace": self.edit_pace_input.text() or "0"
        }
        try:
            exercise["sets"] = int(exercise["sets"])
            exercise["reps"] = int(exercise["reps"])
            exercise["weight"] = float(exercise["weight"])
            exercise["distance"] = float(exercise["distance"])
            exercise["pace"] = float(exercise["pace"])
            self.exercises.append(exercise)
            self.edit_exercise_list_label.setText(f"Добавленные упражнения: {len(self.exercises)}")
            self.edit_exercise_name.setCurrentIndex(-1)
            self.edit_sets_input.clear()
            self.edit_reps_input.clear()
            self.edit_weight_input.clear()
            self.edit_distance_input.clear()
            self.edit_pace_input.clear()
            self.edit_status_label.setText(f"Добавлено упражнение: {exercise_name}")
        except ValueError:
            self.edit_status_label.setText("Ошибка: введите корректные числа")

    def clear_exercise_list(self):
        self.exercises.clear()
        self.exercise_list_label.setText("Добавленные упражнения: 0")
        self.status_label.setText("Список упражнений очищен")

    def clear_edit_exercise_list(self):
        self.exercises.clear()
        self.edit_exercise_list_label.setText("Добавленные упражнения: 0")
        self.edit_status_label.setText("Список упражнений очищен")

    def save_template(self):
        template_name = self.template_name_input.text().strip()
        training_type = self.type_input.currentText()
        duration = self.duration_input.text() or "0"
        if not template_name:
            self.status_label.setText("Введите название шаблона")
            return
        try:
            duration = int(duration)
            if duration <= 0:
                raise ValueError("Длительность должна быть больше 0")
            if not self.exercises:
                raise ValueError("Добавьте хотя бы одно упражнение")
            self.db.add_training_template(self.user["id"], template_name, training_type, duration, self.exercises)
            self.populate_templates()
            self.template_name_input.clear()
            self.status_label.setText(f"Шаблон '{template_name}' сохранен")
        except ValueError as e:
            self.status_label.setText(f"Ошибка: {str(e)}")

    def calculate_calories(self, training_type, duration, exercises):
        # Получаем профиль пользователя
        profile = self.db.get_user_profile(self.user["id"])
        weight = profile[0] if profile else 70.0  # Вес, кг
        height = profile[1] if profile else 170.0  # Рост, см
        age = profile[2] if profile else 30  # Возраст, годы
        gender = profile[3] if profile else "М"  # Пол

        # 1. Базовый метаболизм (BMR) с учётом активности
        if gender == "М":
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        # Увеличиваем BMR на коэффициент активности (1.2 для тренировки)
        bmr_calories = bmr * 1.2 * (duration / 60.0) / 24.0

        # 2. Калории от типа тренировки
        type_id = next((t[0] for t in self.db.get_training_types() if t[1] == training_type), 1)
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT met FROM training_types WHERE id = ?", (type_id,))
        result = cursor.fetchone()
        training_met = result[0] if result else 5.0
        training_calories = training_met * weight * (duration / 60.0)

        # 3. Калории от упражнений
        exercise_calories = 0
        for ex in exercises:
            cursor.execute("SELECT met FROM exercises WHERE name = ?", (ex["name"],))
            result = cursor.fetchone()
            ex_met = result[0] if result else training_met

            if ex["distance"] > 0 and ex["pace"] > 0:
                # Кардио: учитываем дистанцию и темп
                speed = ex["distance"] / (ex["pace"] / 60.0)  # км/ч
                time_hours = ex["distance"] / speed
                # Модификатор интенсивности: быстрее темп (меньше pace) → больше MET
                intensity_modifier = max(1.0, 6.0 / ex["pace"])  # Например, темп 6 мин/км → 1.0, 3 мин/км → 2.0
                exercise_calories += ex_met * weight * time_hours * intensity_modifier
            elif ex["sets"] > 0 and ex["reps"] > 0:
                # Силовые: учитываем подходы, повторения и вес снаряда
                time_hours = ex["sets"] * ex["reps"] * 4 / 3600  # 4 секунды на повторение
                rest_time_hours = ex["sets"] * 60 / 3600  # 60 секунд отдыха на подход
                total_time_hours = time_hours + rest_time_hours
                # Учитываем вес снаряда относительно веса тела
                weight_factor = 1.0 + (ex["weight"] / (weight * 10.0))  # +1% за каждые 10 кг относительно веса тела
                exercise_calories += ex_met * weight * total_time_hours * weight_factor

        # Итог
        total_calories = bmr_calories + training_calories + exercise_calories
        return max(total_calories, 0)  # Гарантируем неотрицательное значение

    def add_training(self):
        training_type = self.type_input.currentText()
        if not training_type:
            self.status_label.setText("Ошибка: выберите тип тренировки")
            QMessageBox.warning(self, "Ошибка", "Выберите тип тренировки")
            return

        duration = self.duration_input.text() or "0"
        date = self.date_selector.date().toString("yyyy-MM-dd")
        try:
            duration = int(duration)
            if duration <= 0:
                raise ValueError("Длительность должна быть больше 0")
            type_id = next((t[0] for t in self.db.get_training_types() if t[1] == training_type), 1)
            calories = self.calculate_calories(training_type, duration, self.exercises)
            training_id = self.db.add_training(self.user["id"], date, type_id, duration, calories)

            for exercise in self.exercises:
                exercise_id = self.db.add_exercise_if_not_exists(exercise["name"], type_id)
                self.db.add_training_exercise(
                    training_id, exercise_id, exercise["sets"], exercise["reps"],
                    exercise["weight"], exercise["distance"], exercise["pace"]
                )
            self.status_label.setText(f"Добавлено: {training_type} ({duration} мин, {calories:.1f} ккал)")
            self.exercises.clear()
            self.exercise_list_label.setText("Добавленные упражнения: 0")
            self.duration_input.clear()
            self.type_input.setCurrentIndex(0)
            self.update_training_list()
            self.update_analytics()
            self.check_achievements()
        except ValueError as e:
            self.status_label.setText(f"Ошибка: {str(e)}")
            QMessageBox.warning(self, "Ошибка", f"Ошибка: {str(e)}")
        except Exception as e:
            self.status_label.setText(f"Неожиданная ошибка: {str(e)}")
            QMessageBox.warning(self, "Ошибка", f"Неожиданная ошибка: {str(e)}")

    def enable_edit_delete_buttons(self):
        self.edit_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)

    def edit_training(self):
        selected_items = self.training_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите тренировку для редактирования")
            return
        selected_text = selected_items[0].text()
        if not selected_text.startswith("  Упражнение"):
            training_type = selected_text.split(":")[0]
            duration = int(selected_text.split(" мин")[0].split(": ")[1])
            date = self.date_selector.date().toString("yyyy-MM-dd")
            type_id = next((t[0] for t in self.db.get_training_types() if t[1] == training_type), 1)
            cursor = self.db.conn.cursor()
            cursor.execute(
                "SELECT id FROM trainings WHERE user_id = ? AND date = ? AND type_id = ? AND duration = ?",
                (self.user["id"], date, type_id, duration)
            )
            training_id = cursor.fetchone()
            if training_id:
                self.editing_training_id = training_id[0]
                training = self.db.get_training(training_id[0])
                exercises = self.db.get_training_exercises(training_id[0])
                self.exercises.clear()
                for ex in exercises:
                    self.exercises.append({
                        "name": ex[0], "sets": ex[1], "reps": ex[2], "weight": ex[3],
                        "distance": ex[4], "pace": ex[5]
                    })
                self.edit_type_input.setCurrentText(training[3])
                self.edit_duration_input.setText(str(training[1]))
                self.edit_exercise_list_label.setText(f"Добавленные упражнения: {len(self.exercises)}")
                self.edit_status_label.setText("Редактируйте данные и сохраните")
                self.update_edit_exercise_form()
                self.tabs.setCurrentWidget(self.edit_tab)

    def delete_training(self):
        selected_items = self.training_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите тренировку для удаления")
            return
        selected_text = selected_items[0].text()
        if not selected_text.startswith("  Упражнение"):
            training_type = selected_text.split(":")[0]
            duration = int(selected_text.split(" мин")[0].split(": ")[1])
            date = self.date_selector.date().toString("yyyy-MM-dd")
            type_id = next((t[0] for t in self.db.get_training_types() if t[1] == training_type), 1)
            cursor = self.db.conn.cursor()
            cursor.execute(
                "SELECT id FROM trainings WHERE user_id = ? AND date = ? AND type_id = ? AND duration = ?",
                (self.user["id"], date, type_id, duration)
            )
            training_id = cursor.fetchone()
            if training_id:
                reply = QMessageBox.question(self, "Подтверждение", "Удалить эту тренировку?",
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.db.delete_training(training_id[0])
                    self.update_training_list()
                    self.update_analytics()
                    self.edit_btn.setEnabled(False)
                    self.delete_btn.setEnabled(False)
                    self.status_label.setText("Тренировка удалена")

    def save_edited_training(self):
        if not self.editing_training_id:
            self.edit_status_label.setText("Ошибка: выберите тренировку для редактирования")
            return
        training_type = self.edit_type_input.currentText()
        duration = self.edit_duration_input.text() or "0"
        try:
            duration = int(duration)
            if duration <= 0:
                raise ValueError("Длительность должна быть больше 0")
            type_id = next((t[0] for t in self.db.get_training_types() if t[1] == training_type), 1)
            calories = self.calculate_calories(training_type, duration, self.exercises)
            self.db.update_training(self.editing_training_id, type_id, duration, calories)
            self.db.delete_training_exercises(self.editing_training_id)
            for exercise in self.exercises:
                cursor = self.db.conn.cursor()
                cursor.execute("SELECT id FROM exercises WHERE name = ?", (exercise["name"],))
                result = cursor.fetchone()
                exercise_id = result[0] if result else 1
                self.db.add_training_exercise(
                    self.editing_training_id, exercise_id, exercise["sets"], exercise["reps"],
                    exercise["weight"], exercise["distance"], exercise["pace"]
                )
            self.edit_status_label.setText(f"Сохранено: {training_type} ({duration} мин, {calories:.1f} ккал)")
            self.exercises.clear()
            self.edit_exercise_list_label.setText("Добавленные упражнения: 0")
            self.editing_training_id = None
            self.update_training_list()
            self.update_analytics()
            self.check_achievements()
        except ValueError as e:
            self.edit_status_label.setText(f"Ошибка: {str(e)}")

    def update_training_list(self):
        self.training_list.clear()
        date = self.date_selector.date().toString("yyyy-MM-dd")
        trainings = self.db.get_trainings_by_date(self.user["id"], date)
        for training in trainings:
            item = QListWidgetItem(f"{training[1]}: {training[2]} мин, {training[3]:.1f} ккал")
            item.setForeground(QColor("#00C8FF") if training[1] in self.cardio_types else QColor("#DCDCDC"))
            self.training_list.addItem(item)
            exercises = self.db.get_training_exercises(training[0])
            for ex in exercises:
                ex_str = f"  Упражнение: {ex[0]}"
                if ex[1] or ex[2] or ex[3]:
                    ex_str += f" ({ex[1]} подходов, {ex[2]} повторений, {ex[3]} кг)"
                if ex[4] or ex[5]:
                    ex_str += f" ({ex[4]} км, темп {ex[5]} мин/км)"
                self.training_list.addItem(ex_str)

    def prev_day(self):
        self.date_selector.setDate(self.date_selector.date().addDays(-1))
        self.update_training_list()
        self.update_analytics()

    def next_day(self):
        self.date_selector.setDate(self.date_selector.date().addDays(1))
        self.update_training_list()
        self.update_analytics()

    def update_analytics(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        start_date = self.date_selector.date().addDays(-6).toString("yyyy-MM-dd")
        end_date = self.date_selector.date().toString("yyyy-MM-dd")
        cursor = self.db.conn.cursor()
        cursor.execute(
            "SELECT date, duration, calories FROM trainings WHERE user_id = ? AND date BETWEEN ? AND ? ORDER BY date",
            (self.user["id"], start_date, end_date)
        )
        training_data = cursor.fetchall()

        if training_data:
            dates = [row[0][-5:] for row in training_data]
            durations = [row[1] for row in training_data]
            calories = [row[2] for row in training_data]
            ax.bar(dates, durations, width=0.4, label="Длительность (мин)", color="#00C8FF")
            ax.bar([i + 0.4 for i in range(len(dates))], calories, width=0.4, label="Калории (ккал)", color="#FF6347")
            ax.legend()
            ax.set_xticks(range(len(dates)))
            ax.set_xticklabels(dates, rotation=45)
            for i, v in enumerate(durations):
                ax.text(i, v + 1, str(v), ha='center')
            for i, v in enumerate(calories):
                ax.text(i + 0.4, v + 1, f"{v:.1f}", ha='center')

        stats = self.db.get_training_stats(self.user["id"], start_date, end_date)
        stats_text = "Статистика по типам тренировок:\n"
        for stat in stats:
            stats_text += f"{stat[0]}: {stat[1]} мин, {stat[2]:.1f} ккал\n"
        self.stats_label.setText(stats_text)

        ax.set_title("Прогресс тренировок за неделю")
        ax.set_xlabel("Дата")
        ax.set_ylabel("Значение")
        self.figure.tight_layout()
        self.canvas.draw()

    def check_achievements(self):
        cursor = self.db.conn.cursor()
        cursor.execute(
            "SELECT SUM(duration) FROM trainings WHERE user_id = ? AND type_id = (SELECT id FROM training_types WHERE name = 'Бег')",
            (self.user["id"],)
        )
        total_running = cursor.fetchone()[0] or 0
        if total_running >= 300:
            cursor.execute(
                "SELECT COUNT(*) FROM achievements WHERE user_id = ? AND name = ?",
                (self.user["id"], "300 минут бега")
            )
            if cursor.fetchone()[0] == 0:
                self.db.add_achievement(self.user["id"], "300 минут бега")
                self.status_label.setText("Достижение: 300 минут бега!")

        cursor.execute(
            "SELECT DISTINCT date FROM trainings WHERE user_id = ? AND date >= date('now', '-5 days')",
            (self.user["id"],)
        )
        dates = cursor.fetchall()
        if len(dates) >= 5:
            cursor.execute(
                "SELECT COUNT(*) FROM achievements WHERE user_id = ? AND name = ?",
                (self.user["id"], "5 дней подряд")
            )
            if cursor.fetchone()[0] == 0:
                self.db.add_achievement(self.user["id"], "5 дней подряд")
                self.status_label.setText("Достижение: 5 дней подряд!")

    def populate_templates(self):
        self.template_selector.clear()
        self.template_selector.addItem("")
        templates = self.db.get_training_templates(self.user["id"])
        self.template_selector.addItems([t[1] for t in templates])

    def apply_template(self):
        template_name = self.template_selector.currentText()
        if template_name:
            cursor = self.db.conn.cursor()
            cursor.execute(
                "SELECT id, type, duration FROM training_templates WHERE name = ?",
                (template_name,)
            )
            result = cursor.fetchone()
            if result:
                template_id, training_type, duration = result
                self.type_input.setCurrentText(training_type)
                self.duration_input.setText(str(duration))
                self.exercises.clear()
                exercises = self.db.get_template_exercises(template_id)
                for ex in exercises:
                    self.exercises.append({
                        "name": ex[0], "sets": ex[1], "reps": ex[2],
                        "weight": ex[3], "distance": ex[4], "pace": ex[5]
                    })
                self.exercise_list_label.setText(f"Добавленные упражнения: {len(self.exercises)}")
                self.update_exercise_form()
                self.status_label.setText(f"Применен шаблон: {template_name}")

    def repeat_last_training(self):
        cursor = self.db.conn.cursor()
        cursor.execute(
            "SELECT id, type_id, duration FROM trainings WHERE user_id = ? ORDER BY date DESC LIMIT 1",
            (self.user["id"],)
        )
        result = cursor.fetchone()
        if result:
            training_id, type_id, duration = result
            cursor.execute("SELECT name FROM training_types WHERE id = ?", (type_id,))
            training_type = cursor.fetchone()[0]
            self.type_input.setCurrentText(training_type)
            self.duration_input.setText(str(duration))
            self.exercises.clear()
            exercises = self.db.get_training_exercises(training_id)
            for ex in exercises:
                self.exercises.append({
                    "name": ex[0], "sets": ex[1], "reps": ex[2],
                    "weight": ex[3], "distance": ex[4], "pace": ex[5]
                })
            self.exercise_list_label.setText(f"Добавленные упражнения: {len(self.exercises)}")
            self.update_exercise_form()
            self.status_label.setText("Загружена последняя тренировка")
        else:
            self.status_label.setText("Нет предыдущих тренировок")