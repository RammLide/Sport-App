from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QHBoxLayout, QComboBox, QListWidget, QDateEdit, QTabWidget, QMessageBox, QFormLayout, QListWidgetItem, QSizePolicy, QGridLayout, QScrollArea
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QColor, QIcon
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
        main_layout = QVBoxLayout()

        # Вкладки
        self.tabs = QTabWidget()
        self.add_tab = QWidget()
        self.view_tab = QWidget()
        self.edit_tab = QWidget()
        self.analytics_tab = QWidget()
        self.tabs.addTab(self.add_tab, "Добавить тренировку")
        self.tabs.addTab(self.view_tab, "Просмотр")
        self.tabs.addTab(self.edit_tab, "Редактировать тренировку")
        self.tabs.addTab(self.analytics_tab, QIcon("icons/analytics.png"), "Аналитика")
        main_layout.addWidget(self.tabs)

        # Вкладка "Добавить тренировку"
        add_scroll = QScrollArea()
        add_scroll.setWidgetResizable(True)
        add_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        add_scroll.setStyleSheet("""
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

        add_inner_widget = QWidget()
        add_inner_layout = QVBoxLayout(add_inner_widget)
        add_inner_layout.setSpacing(15)
        add_inner_layout.setAlignment(Qt.AlignTop)

        # Заголовок
        title_label = QLabel("Добавить тренировку")
        title_label.setAccessibleName("header")
        add_inner_layout.addWidget(title_label)

        # Выбор шаблона
        template_label = QLabel("Выбрать шаблон:")
        template_label.setAccessibleName("small")
        self.template_selector = QComboBox(self)
        self.template_selector.setMinimumWidth(300)
        self.template_selector.setFixedHeight(30)
        self.populate_templates()
        self.template_selector.currentTextChanged.connect(self.apply_template)
        add_inner_layout.addWidget(template_label)
        add_inner_layout.addWidget(self.template_selector)

        # Кнопка "Удалить шаблон"
        delete_template_btn = QPushButton("Удалить шаблон")
        delete_template_btn.setMinimumWidth(200)
        delete_template_btn.setFixedHeight(30)
        delete_template_btn.setIcon(QIcon("icons/delete.png"))
        delete_template_btn.setStyleSheet("""
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
        delete_template_btn.clicked.connect(self.delete_template)
        delete_template_layout = QHBoxLayout()
        delete_template_layout.addStretch()
        delete_template_layout.addWidget(delete_template_btn)
        delete_template_layout.addStretch()
        add_inner_layout.addLayout(delete_template_layout)

        # Тип тренировки и длительность (используем QGridLayout)
        training_form = QGridLayout()
        training_form.setHorizontalSpacing(10)
        training_form.setVerticalSpacing(10)

        type_label = QLabel("Тип тренировки:")
        type_label.setAccessibleName("small")
        self.type_input = QComboBox(self)
        self.type_input.setMinimumWidth(300)
        self.type_input.setFixedHeight(30)
        training_types = self.db.get_training_types()
        self.type_input.addItems([t[1] for t in training_types])
        self.type_input.setCurrentText("Бег")  # Устанавливаем "Бег" по умолчанию
        self.type_input.currentTextChanged.connect(self.update_exercise_form)

        duration_label = QLabel("Длительность:")
        duration_label.setAccessibleName("small")
        self.duration_input = QLineEdit(self)
        self.duration_input.setPlaceholderText("Длительность (мин)")
        self.duration_input.setMinimumWidth(300)
        self.duration_input.setFixedHeight(30)

        training_form.addWidget(type_label, 0, 0)
        training_form.addWidget(self.type_input, 0, 1)
        training_form.addWidget(duration_label, 1, 0)
        training_form.addWidget(self.duration_input, 1, 1)

        add_inner_layout.addLayout(training_form)

        # Форма для упражнений
        exercise_label = QLabel("Добавить упражнение:")
        exercise_label.setAccessibleName("small")
        add_inner_layout.addWidget(exercise_label)

        self.exercise_form = QGridLayout()
        self.exercise_form.setHorizontalSpacing(10)
        self.exercise_form.setVerticalSpacing(10)

        self.exercise_name_label = QLabel("Упражнение:")
        self.exercise_name = QComboBox(self)
        self.exercise_name.setEditable(True)
        self.exercise_name.setMinimumWidth(300)
        self.exercise_name.setFixedHeight(30)
        self.exercise_form.addWidget(self.exercise_name_label, 0, 0)
        self.exercise_form.addWidget(self.exercise_name, 0, 1)

        self.sets_label = QLabel("Подходы:")
        self.sets_input = QLineEdit(self)
        self.sets_input.setPlaceholderText("Подходы")
        self.sets_input.setMinimumWidth(300)
        self.sets_input.setFixedHeight(30)
        self.exercise_form.addWidget(self.sets_label, 1, 0)
        self.exercise_form.addWidget(self.sets_input, 1, 1)

        self.reps_label = QLabel("Повторения:")
        self.reps_input = QLineEdit(self)
        self.reps_input.setPlaceholderText("Повторения")
        self.reps_input.setMinimumWidth(300)
        self.reps_input.setFixedHeight(30)
        self.exercise_form.addWidget(self.reps_label, 2, 0)
        self.reps_input.setVisible(False)
        self.exercise_form.addWidget(self.reps_input, 2, 1)

        self.weight_label = QLabel("Вес (кг):")
        self.weight_input = QLineEdit(self)
        self.weight_input.setPlaceholderText("Вес (кг)")
        self.weight_input.setMinimumWidth(300)
        self.weight_input.setFixedHeight(30)
        self.exercise_form.addWidget(self.weight_label, 3, 0)
        self.exercise_form.addWidget(self.weight_input, 3, 1)

        self.distance_label = QLabel("Дистанция (км):")
        self.distance_input = QLineEdit(self)
        self.distance_input.setPlaceholderText("Дистанция (км)")
        self.distance_input.setMinimumWidth(300)
        self.distance_input.setFixedHeight(30)
        self.exercise_form.addWidget(self.distance_label, 4, 0)
        self.distance_input.setVisible(False)
        self.exercise_form.addWidget(self.distance_input, 4, 1)

        self.pace_label = QLabel("Темп (мин/км):")
        self.pace_input = QLineEdit(self)
        self.pace_input.setPlaceholderText("Темп (мин/км)")
        self.pace_input.setMinimumWidth(300)
        self.pace_input.setFixedHeight(30)
        self.exercise_form.addWidget(self.pace_label, 5, 0)
        self.pace_input.setVisible(False)
        self.exercise_form.addWidget(self.pace_input, 5, 1)

        add_inner_layout.addLayout(self.exercise_form)

        # Кнопки для упражнений
        add_exercise_btn = QPushButton("Добавить упражнение в список")
        add_exercise_btn.setAccessibleName("action")
        add_exercise_btn.setIcon(QIcon("icons/add.png"))
        add_exercise_btn.setMinimumWidth(200)
        add_exercise_btn.setFixedHeight(30)
        add_exercise_btn.setStyleSheet("""
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
        add_exercise_btn.clicked.connect(self.add_exercise_to_list)
        add_exercise_layout = QHBoxLayout()
        add_exercise_layout.addStretch()
        add_exercise_layout.addWidget(add_exercise_btn)
        add_exercise_layout.addStretch()
        add_inner_layout.addLayout(add_exercise_layout)

        clear_exercises_btn = QPushButton("Очистить список упражнений")
        clear_exercises_btn.setMinimumWidth(200)
        clear_exercises_btn.setFixedHeight(30)
        clear_exercises_btn.setStyleSheet("""
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
        clear_exercises_btn.clicked.connect(self.clear_exercise_list)
        clear_exercises_layout = QHBoxLayout()
        clear_exercises_layout.addStretch()
        clear_exercises_layout.addWidget(clear_exercises_btn)
        clear_exercises_layout.addStretch()
        add_inner_layout.addLayout(clear_exercises_layout)

        self.exercise_list_label = QLabel("Добавленные упражнения: 0")
        self.exercise_list_label.setAccessibleName("small")
        add_inner_layout.addWidget(self.exercise_list_label)

        # Сохранение шаблона
        template_name_label = QLabel("Название шаблона:")
        template_name_label.setAccessibleName("small")
        self.template_name_input = QLineEdit(self)
        self.template_name_input.setPlaceholderText("Название шаблона")
        self.template_name_input.setMinimumWidth(300)
        self.template_name_input.setFixedHeight(30)
        add_inner_layout.addWidget(template_name_label)
        add_inner_layout.addWidget(self.template_name_input)

        save_template_btn = QPushButton("Сохранить как шаблон")
        save_template_btn.setMinimumWidth(200)
        save_template_btn.setFixedHeight(30)
        save_template_btn.setIcon(QIcon("icons/save.png"))
        save_template_btn.setStyleSheet("""
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
        save_template_btn.clicked.connect(self.save_template)
        save_template_layout = QHBoxLayout()
        save_template_layout.addStretch()
        save_template_layout.addWidget(save_template_btn)
        save_template_layout.addStretch()
        add_inner_layout.addLayout(save_template_layout)

        # Кнопки для сохранения тренировки
        add_btn = QPushButton("Сохранить тренировку")
        add_btn.setAccessibleName("action")
        add_btn.setMinimumWidth(200)
        add_btn.setFixedHeight(30)
        add_btn.setIcon(QIcon("icons/save.png"))
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
        add_btn.clicked.connect(self.add_training)
        add_btn_layout = QHBoxLayout()
        add_btn_layout.addStretch()
        add_btn_layout.addWidget(add_btn)
        add_btn_layout.addStretch()
        add_inner_layout.addLayout(add_btn_layout)

        repeat_btn = QPushButton("Повторить последнюю")
        repeat_btn.setMinimumWidth(200)
        repeat_btn.setFixedHeight(30)
        repeat_btn.setIcon(QIcon("icons/repeat.png"))
        repeat_btn.setStyleSheet("""
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
        repeat_btn.clicked.connect(self.repeat_last_training)
        repeat_btn_layout = QHBoxLayout()
        repeat_btn_layout.addStretch()
        repeat_btn_layout.addWidget(repeat_btn)
        repeat_btn_layout.addStretch()
        add_inner_layout.addLayout(repeat_btn_layout)

        self.status_label = QLabel("Введите данные тренировки")
        self.status_label.setAccessibleName("small")
        add_inner_layout.addWidget(self.status_label)
        add_inner_layout.addStretch()

        # Устанавливаем содержимое QScrollArea
        add_scroll.setWidget(add_inner_widget)
        add_layout = QVBoxLayout()
        add_layout.addWidget(add_scroll)
        self.add_tab.setLayout(add_layout)

        # Вкладка "Просмотр"
        view_inner_layout = QVBoxLayout()
        view_inner_layout.setSpacing(15)
        view_inner_layout.setAlignment(Qt.AlignTop)

        self.date_selector = QDateEdit(self)
        self.date_selector.setCalendarPopup(True)
        self.date_selector.setDate(QDate.currentDate())
        self.date_selector.dateChanged.connect(self.update_training_list)
        self.date_selector.setMinimumWidth(150)
        self.date_selector.setFixedHeight(30)
        self.date_selector.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        nav_layout = QHBoxLayout()
        prev_btn = QPushButton("Предыдущий день")
        prev_btn.setMinimumWidth(150)
        prev_btn.setFixedHeight(30)
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
        next_btn = QPushButton("Следующий день")
        next_btn.setMinimumWidth(150)
        next_btn.setFixedHeight(30)
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
        nav_layout.addWidget(prev_btn)
        nav_layout.addWidget(self.date_selector)
        nav_layout.addWidget(next_btn)

        training_list_label = QLabel("Добавленные тренировки:")
        training_list_label.setAccessibleName("small")
        self.training_list = QListWidget(self)
        self.training_list.itemClicked.connect(self.enable_edit_delete_buttons)

        action_layout = QHBoxLayout()
        self.edit_btn = QPushButton("Изменить")
        self.edit_btn.setIcon(QIcon("icons/edit.png"))
        self.edit_btn.setMinimumWidth(150)
        self.edit_btn.setFixedHeight(30)
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
        self.edit_btn.clicked.connect(self.edit_training)
        self.edit_btn.setEnabled(False)

        self.delete_btn = QPushButton("Удалить")
        self.delete_btn.setIcon(QIcon("icons/delete.png"))
        self.delete_btn.setMinimumWidth(150)
        self.delete_btn.setFixedHeight(30)
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
        self.delete_btn.clicked.connect(self.delete_training)
        self.delete_btn.setEnabled(False)
        action_layout.addWidget(self.edit_btn)
        action_layout.addWidget(self.delete_btn)

        view_inner_layout.addLayout(nav_layout)
        view_inner_layout.addWidget(training_list_label)
        view_inner_layout.addWidget(self.training_list)
        view_inner_layout.addLayout(action_layout)
        view_inner_layout.addStretch()

        view_layout = QHBoxLayout()
        view_layout.setAlignment(Qt.AlignCenter)
        view_inner_widget = QWidget()
        view_inner_widget.setLayout(view_inner_layout)
        view_layout.addWidget(view_inner_widget)
        self.view_tab.setLayout(view_layout)
        self.update_training_list()

        # Вкладка "Редактировать тренировку"
        edit_scroll = QScrollArea()
        edit_scroll.setWidgetResizable(True)
        edit_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        edit_scroll.setStyleSheet("""
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

        edit_inner_widget = QWidget()
        edit_inner_layout = QVBoxLayout(edit_inner_widget)
        edit_inner_layout.setSpacing(15)
        edit_inner_layout.setAlignment(Qt.AlignTop)

        edit_title_label = QLabel("Редактировать тренировку")
        edit_title_label.setAccessibleName("header")
        edit_inner_layout.addWidget(edit_title_label)

        edit_training_form = QGridLayout()
        edit_training_form.setHorizontalSpacing(10)
        edit_training_form.setVerticalSpacing(10)

        edit_type_label = QLabel("Тип тренировки:")
        edit_type_label.setAccessibleName("small")
        self.edit_type_input = QComboBox(self)
        self.edit_type_input.setMinimumWidth(300)
        self.edit_type_input.setFixedHeight(30)
        self.edit_type_input.addItems([t[1] for t in training_types])
        self.edit_type_input.currentTextChanged.connect(self.update_edit_exercise_form)

        edit_duration_label = QLabel("Длительность:")
        edit_duration_label.setAccessibleName("small")
        self.edit_duration_input = QLineEdit(self)
        self.edit_duration_input.setPlaceholderText("Длительность (мин)")
        self.edit_duration_input.setMinimumWidth(300)
        self.edit_duration_input.setFixedHeight(30)

        edit_training_form.addWidget(edit_type_label, 0, 0)
        edit_training_form.addWidget(self.edit_type_input, 0, 1)
        edit_training_form.addWidget(edit_duration_label, 1, 0)
        edit_training_form.addWidget(self.edit_duration_input, 1, 1)

        edit_inner_layout.addLayout(edit_training_form)

        edit_exercise_label = QLabel("Добавить упражнение:")
        edit_exercise_label.setAccessibleName("small")
        self.edit_exercise_form = QGridLayout()
        self.edit_exercise_form.setHorizontalSpacing(10)
        self.edit_exercise_form.setVerticalSpacing(10)

        self.edit_exercise_name_label = QLabel("Упражнение:")
        self.edit_exercise_name = QComboBox(self)
        self.edit_exercise_name.setEditable(True)
        self.edit_exercise_name.setMinimumWidth(300)
        self.edit_exercise_name.setFixedHeight(30)
        self.edit_exercise_form.addWidget(self.edit_exercise_name_label, 0, 0)
        self.edit_exercise_name.addItems([e[1] for e in self.db.get_exercises_by_type(1)])
        self.edit_exercise_form.addWidget(self.edit_exercise_name, 0, 1)

        self.edit_sets_label = QLabel("Подходы:")
        self.edit_sets_input = QLineEdit(self)
        self.edit_sets_input.setPlaceholderText("Подходы")
        self.edit_sets_input.setMinimumWidth(300)
        self.edit_sets_input.setFixedHeight(30)
        self.edit_exercise_form.addWidget(self.edit_sets_label, 1, 0)
        self.edit_sets_input.setVisible(False)
        self.edit_exercise_form.addWidget(self.edit_sets_input, 1, 1)

        self.edit_reps_label = QLabel("Повторения:")
        self.edit_reps_input = QLineEdit(self)
        self.edit_reps_input.setPlaceholderText("Повторения")
        self.edit_reps_input.setMinimumWidth(300)
        self.edit_reps_input.setFixedHeight(30)
        self.edit_exercise_form.addWidget(self.edit_reps_label, 2, 0)
        self.edit_reps_input.setVisible(False)
        self.edit_exercise_form.addWidget(self.edit_reps_input, 2, 1)

        self.edit_weight_label = QLabel("Вес (кг):")
        self.edit_weight_input = QLineEdit(self)
        self.edit_weight_input.setPlaceholderText("Вес (кг)")
        self.edit_weight_input.setMinimumWidth(300)
        self.edit_weight_input.setFixedHeight(30)
        self.edit_exercise_form.addWidget(self.edit_weight_label, 3, 0)
        self.edit_weight_input.setVisible(True)
        self.edit_exercise_form.addWidget(self.edit_weight_input, 3, 1)

        self.edit_distance_label = QLabel("Дистанция (км):")
        self.edit_distance_input = QLineEdit(self)
        self.edit_distance_input.setPlaceholderText("Дистанция (км)")
        self.edit_distance_input.setMinimumWidth(300)
        self.edit_distance_input.setFixedHeight(30)
        self.edit_exercise_form.addWidget(self.edit_distance_label, 4, 0)
        self.edit_distance_input.setVisible(False)
        self.edit_exercise_form.addWidget(self.edit_distance_input, 4, 1)

        self.edit_pace_label = QLabel("Темп (мин/км):")
        self.edit_pace_input = QLineEdit(self)
        self.edit_pace_input.setPlaceholderText("Темп (мин/км)")
        self.edit_pace_input.setMinimumWidth(300)
        self.edit_pace_input.setFixedHeight(30)
        self.edit_exercise_form.addWidget(self.edit_pace_label, 5, 0)
        self.edit_pace_input.setVisible(False)
        self.edit_exercise_form.addWidget(self.edit_pace_input, 5, 1)

        edit_inner_layout.addWidget(edit_exercise_label)
        edit_inner_layout.addLayout(self.edit_exercise_form)

        edit_add_exercise_btn = QPushButton("Добавить упражнение в список")
        edit_add_exercise_btn.setAccessibleName("action")
        edit_add_exercise_btn.setMinimumWidth(200)
        edit_add_exercise_btn.setFixedHeight(30)
        edit_add_exercise_btn.setIcon(QIcon("icons/add.png"))
        edit_add_exercise_btn.setStyleSheet("""
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
        edit_add_exercise_btn.clicked.connect(self.add_edit_exercise_to_list)
        edit_add_exercise_layout = QHBoxLayout()
        edit_add_exercise_layout.addStretch()
        edit_add_exercise_layout.addWidget(edit_add_exercise_btn)
        edit_add_exercise_layout.addStretch()
        edit_inner_layout.addLayout(edit_add_exercise_layout)

        edit_clear_exercises_btn = QPushButton("Очистить список упражнений")
        edit_clear_exercises_btn.setMinimumWidth(200)
        edit_clear_exercises_btn.setFixedHeight(30)
        edit_clear_exercises_btn.setStyleSheet("""
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
        edit_clear_exercises_btn.clicked.connect(self.clear_edit_exercise_list)
        edit_clear_exercises_layout = QHBoxLayout()
        edit_clear_exercises_layout.addStretch()
        edit_clear_exercises_layout.addWidget(edit_clear_exercises_btn)
        edit_clear_exercises_layout.addStretch()
        edit_inner_layout.addLayout(edit_clear_exercises_layout)

        self.edit_exercise_list_label = QLabel("Добавленные упражнения: 0")
        self.edit_exercise_list_label.setAccessibleName("small")
        edit_inner_layout.addWidget(self.edit_exercise_list_label)

        save_edit_btn = QPushButton("Сохранить изменения")
        save_edit_btn.setAccessibleName("action")
        save_edit_btn.setMinimumWidth(200)
        save_edit_btn.setFixedHeight(30)
        save_edit_btn.setIcon(QIcon("icons/save.png"))
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
        save_edit_btn.clicked.connect(self.save_edited_training)
        save_edit_btn_layout = QHBoxLayout()
        save_edit_btn_layout.addStretch()
        save_edit_btn_layout.addWidget(save_edit_btn)
        save_edit_btn_layout.addStretch()
        edit_inner_layout.addLayout(save_edit_btn_layout)

        self.edit_status_label = QLabel("Выберите тренировку для редактирования")
        self.edit_status_label.setAccessibleName("small")
        edit_inner_layout.addWidget(self.edit_status_label)
        edit_inner_layout.addStretch()

        edit_scroll.setWidget(edit_inner_widget)
        edit_layout = QVBoxLayout()
        edit_layout.addWidget(edit_scroll)
        self.edit_tab.setLayout(edit_layout)

        # Вкладка "Аналитика"
        analytics_scroll = QScrollArea()
        analytics_scroll.setWidgetResizable(True)
        analytics_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        analytics_scroll.setStyleSheet("""
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

        analytics_inner_widget = QWidget()
        analytics_inner_layout = QVBoxLayout(analytics_inner_widget)
        analytics_inner_layout.setSpacing(15)
        analytics_inner_layout.setAlignment(Qt.AlignTop)

        analytics_title_label = QLabel("Аналитика тренировок")
        analytics_title_label.setAccessibleName("header")
        analytics_inner_layout.addWidget(analytics_title_label)

        period_layout = QHBoxLayout()
        period_label = QLabel("Период:")
        period_label.setAccessibleName("small")
        self.period_selector = QComboBox()
        self.period_selector.addItems(["Неделя", "Месяц", "Год"])
        self.period_selector.currentTextChanged.connect(self.update_analytics)
        period_layout.addWidget(period_label)
        period_layout.addWidget(self.period_selector)
        period_layout.addStretch()
        analytics_inner_layout.addLayout(period_layout)

        # Создаем контейнер для графика с фиксированной высотой
        self.figure = plt.Figure(figsize=(14, 6))  # Увеличиваем ширину фигуры
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setFixedHeight(400)  # Фиксированная высота графика в пикселях
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        analytics_inner_layout.addWidget(self.canvas)

        self.stats_label = QLabel("Статистика по типам тренировок:")
        self.stats_label.setAccessibleName("header")
        analytics_inner_layout.addWidget(self.stats_label)

        analytics_inner_layout.addStretch()  # Добавляем растяжение внизу, чтобы содержимое не растягивалось

        analytics_scroll.setWidget(analytics_inner_widget)
        analytics_layout = QVBoxLayout()  # Изменяем на QVBoxLayout для лучшей прокрутки
        analytics_layout.addWidget(analytics_scroll)
        self.analytics_tab.setLayout(analytics_layout)
        self.update_analytics()

        # Устанавливаем основной макет для виджета
        self.setLayout(main_layout)
        # Вызываем update_exercise_form после инициализации UI для корректной настройки формы
        self.update_exercise_form()

    def update_exercise_form(self):
        training_type = self.type_input.currentText()
        is_cardio = training_type in self.cardio_types
        type_id = next((t[0] for t in self.db.get_training_types() if t[1] == training_type), 1)
        # Очищаем текущий список упражнений
        self.exercise_name.clear()
        # Получаем уникальные упражнения для выбранного типа
        exercises = sorted(set([e[1] for e in self.db.get_exercises_by_type(type_id)]))
        self.exercise_name.addItems(exercises)
        # Управляем видимостью полей
        self.sets_input.setVisible(not is_cardio)
        self.reps_input.setVisible(not is_cardio)
        self.weight_input.setVisible(not is_cardio)
        self.distance_input.setVisible(is_cardio)
        self.pace_input.setVisible(is_cardio)
        self.sets_label.setVisible(not is_cardio)
        self.reps_label.setVisible(not is_cardio)
        self.weight_label.setVisible(not is_cardio)
        self.distance_label.setVisible(is_cardio)
        self.pace_label.setVisible(is_cardio)
        # Очищаем поля ввода для избежания путаницы
        if is_cardio:
            self.sets_input.clear()
            self.reps_input.clear()
            self.weight_input.clear()
        else:
            self.distance_input.clear()
            self.pace_input.clear()

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
        self.edit_sets_label.setVisible(not is_cardio)
        self.edit_reps_label.setVisible(not is_cardio)
        self.edit_weight_label.setVisible(not is_cardio)
        self.edit_distance_label.setVisible(is_cardio)
        self.edit_pace_label.setVisible(is_cardio)

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
        profile = self.db.get_user_profile(self.user["id"])
        weight = profile[0] if profile else 70.0
        height = profile[1] if profile else 170.0
        age = profile[2] if profile else 30
        gender = profile[3] if profile else "М"

        if gender == "М":
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        bmr_calories = bmr * 1.2 * (duration / 60.0) / 24.0

        type_id = next((t[0] for t in self.db.get_training_types() if t[1] == training_type), 1)
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT met FROM training_types WHERE id = ?", (type_id,))
        result = cursor.fetchone()
        training_met = result[0] if result else 5.0
        training_calories = training_met * weight * (duration / 60.0)

        exercise_calories = 0
        for ex in exercises:
            cursor.execute("SELECT met FROM exercises WHERE name = ?", (ex["name"],))
            result = cursor.fetchone()
            ex_met = result[0] if result else training_met

            if ex["distance"] > 0 and ex["pace"] > 0:
                speed = ex["distance"] / (ex["pace"] / 60.0)
                time_hours = ex["distance"] / speed
                intensity_modifier = max(1.0, 6.0 / ex["pace"])
                exercise_calories += ex_met * weight * time_hours * intensity_modifier
            elif ex["sets"] > 0 and ex["reps"] > 0:
                time_hours = ex["sets"] * ex["reps"] * 4 / 3600
                rest_time_hours = ex["sets"] * 60 / 3600
                total_time_hours = time_hours + rest_time_hours
                weight_factor = 1.0 + (ex["weight"] / (weight * 10.0))
                exercise_calories += ex_met * weight * total_time_hours * weight_factor

        total_calories = bmr_calories + training_calories + exercise_calories
        return max(total_calories, 0)

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

            print(f"Adding training ID: {training_id}, Type: {training_type}, Exercises: {len(self.exercises)}")
            for exercise in self.exercises:
                exercise_id = self.db.add_exercise_if_not_exists(exercise["name"], type_id)
                print(f"Saving exercise: {exercise['name']}, ID: {exercise_id}, Sets: {exercise['sets']}, Reps: {exercise['reps']}, Weight: {exercise['weight']}, Distance: {exercise['distance']}, Pace: {exercise['pace']}")
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

    def repeat_last_training(self):
        last_training = self.db.get_last_training(self.user["id"])
        if not last_training:
            self.status_label.setText("Нет предыдущих тренировок")
            return

        training_id, date, type_id, duration, calories = last_training
        training_type = next((t[1] for t in self.db.get_training_types() if t[0] == type_id), None)
        if not training_type:
            self.status_label.setText("Ошибка: тип тренировки не найден")
            return

        exercises = self.db.get_training_exercises(training_id)
        self.exercises.clear()
        for ex in exercises:
            exercise = {
                "name": ex[1],
                "sets": ex[2],
                "reps": ex[3],
                "weight": ex[4],
                "distance": ex[5],
                "pace": ex[6]
            }
            self.exercises.append(exercise)

        self.type_input.setCurrentText(training_type)
        self.duration_input.setText(str(duration))
        self.exercise_list_label.setText(f"Добавленные упражнения: {len(self.exercises)}")
        self.status_label.setText("Загружена последняя тренировка")

    def update_training_list(self):
        self.training_list.clear()
        date = self.date_selector.date().toString("yyyy-MM-dd")
        trainings = self.db.get_trainings_by_date(self.user["id"], date)

        for training in trainings:
            training_id, training_type, duration, calories = training
            exercises = self.db.get_training_exercises(training_id)
            print(f"Training ID: {training_id}, Type: {training_type}, Exercises: {exercises}")
            item_text = f"{training_type} ({duration} мин, {calories:.1f} ккал)\n"
            if not exercises:
                item_text += "  (Нет упражнений)\n"
            else:
                for ex in exercises:
                    try:
                        exercise_name, sets, reps, weight, distance, pace, _ = ex
                        if distance > 0:
                            item_text += f"  {exercise_name}: {distance} км, темп {pace} мин/км\n"
                        else:
                            item_text += f"  {exercise_name}: {sets} подходов, {reps} повторений, {weight} кг\n"
                    except Exception as e:
                        print(f"Error processing exercise for training {training_id}: {e}")
                        item_text += f"  Ошибка загрузки упражнения: {str(e)}\n"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, training_id)
            self.training_list.addItem(item)

    def prev_day(self):
        current_date = self.date_selector.date()
        self.date_selector.setDate(current_date.addDays(-1))
        self.update_training_list()

    def next_day(self):
        current_date = self.date_selector.date()
        self.date_selector.setDate(current_date.addDays(1))
        self.update_training_list()

    def enable_edit_delete_buttons(self, item):
        self.edit_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)

    def edit_training(self):
        selected_item = self.training_list.currentItem()
        if not selected_item:
            self.edit_status_label.setText("Выберите тренировку для редактирования")
            return

        training_id = selected_item.data(Qt.UserRole)
        training = self.db.get_training_by_id(training_id)
        if not training:
            self.edit_status_label.setText("Ошибка: тренировка не найдена")
            return

        _, _, type_id, duration, _ = training
        training_type = next((t[1] for t in self.db.get_training_types() if t[0] == type_id), None)
        if not training_type:
            self.edit_status_label.setText("Ошибка: тип тренировки не найден")
            return

        exercises = self.db.get_training_exercises(training_id)
        self.exercises.clear()
        for ex in exercises:
            exercise = {
                "name": ex[1],
                "sets": ex[2],
                "reps": ex[3],
                "weight": ex[4],
                "distance": ex[5],
                "pace": ex[6]
            }
            self.exercises.append(exercise)

        self.edit_type_input.setCurrentText(training_type)
        self.edit_duration_input.setText(str(duration))
        self.edit_exercise_list_label.setText(f"Добавленные упражнения: {len(self.exercises)}")
        self.editing_training_id = training_id
        self.edit_status_label.setText("Тренировка загружена для редактирования")
        self.tabs.setCurrentWidget(self.edit_tab)

    def save_edited_training(self):
        if self.editing_training_id is None:
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
                exercise_id = self.db.add_exercise_if_not_exists(exercise["name"], type_id)
                self.db.add_training_exercise(
                    self.editing_training_id, exercise_id, exercise["sets"], exercise["reps"],
                    exercise["weight"], exercise["distance"], exercise["pace"]
                )

            self.edit_status_label.setText(f"Изменено: {training_type} ({duration} мин, {calories:.1f} ккал)")
            self.exercises.clear()
            self.edit_exercise_list_label.setText("Добавленные упражнения: 0")
            self.edit_duration_input.clear()
            self.edit_type_input.setCurrentIndex(0)
            self.editing_training_id = None
            self.update_training_list()
            self.update_analytics()
            self.check_achievements()
            self.tabs.setCurrentWidget(self.view_tab)
        except ValueError as e:
            self.edit_status_label.setText(f"Ошибка: {str(e)}")
            QMessageBox.warning(self, "Ошибка", f"Ошибка: {str(e)}")

    def delete_training(self):
        selected_item = self.training_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Ошибка", "Выберите тренировку для удаления")
            return

        training_id = selected_item.data(Qt.UserRole)
        reply = QMessageBox.question(
            self, "Подтверждение", "Вы уверены, что хотите удалить эту тренировку?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.db.delete_training(training_id)
            self.update_training_list()
            self.update_analytics()
            self.check_achievements()
            self.edit_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)

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

        # Подготовка данных для графика
        dates = [row[0][-5:] for row in training_data]
        durations = [row[1] for row in training_data]
        calories = [row[2] for row in training_data]

        # График
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('none')  # Прозрачный фон подграфика
        ax.tick_params(colors='white', labelsize=6)
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        self.figure.set_facecolor('none')  # Прозрачный фон фигуры

        if training_data:
            x = range(len(dates))
            ax.bar(x, durations, width=0.35, label="Длительность (мин)", color="#00C8FF", edgecolor="#FF9500")
            ax.bar([i + 0.35 for i in x], calories, width=0.35, label="Калории (ккал)", color="#FF6347", edgecolor="#FF9500")
            # Перемещаем легенду ближе к скроллбару с небольшим отступом
            ax.legend(
                fontsize=8,
                labelcolor='white',
                facecolor=(0.1647, 0.1647, 0.1647, 0.9),  # #2A2A2A с прозрачностью 0.9
                edgecolor='#FF9500',  # Оранжевая рамка
                framealpha=0.9,  # Прозрачность рамки
                loc='upper left',
                bbox_to_anchor=(1.03, 1.0)  # Позиция: 15% отступа от правого края графика, верх выровнен с заголовком
            )
            ax.set_xticks(x)
            ax.set_xticklabels(dates, rotation=45, color='white')
            ax.set_title(f"Прогресс тренировок за {period.lower()}", fontsize=8, color='white')
            ax.set_xlabel("Дата", color='white', fontsize=6)
            ax.set_ylabel("Значение", color='white', fontsize=6)

            # Подписи значений с учётом максимума на каждой дате
            for i in range(len(dates)):
                max_height = max(durations[i], calories[i])
                ax.text(i, durations[i] + max_height * 0.05, str(durations[i]), ha='center', color='white', fontsize=6)
                ax.text(i + 0.35, calories[i] + max_height * 0.05, f"{calories[i]:.1f}", ha='center', color='white', fontsize=6)

            # Устанавливаем границы подграфика вручную, чтобы график не растягивался слишком сильно вправо
            ax.set_position([0.1, 0.15, 0.75, 0.75])  # [left, bottom, width, height]

        else:
            ax.text(0.5, 0.5, "Нет данных о тренировках", ha='center', va='center', fontsize=8, color='white')

        # Статистика
        stats_text = "Статистика по типам тренировок:\n"
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

        stats_text += f"Итого: {total_duration} мин, {total_calories:.1f} ккал\n"

        if training_data:
            avg_duration = total_duration / len(training_data)
            avg_calories = total_calories / len(training_data)
            stats_text += f"\nСредняя продолжительность: {avg_duration:.1f} мин\n"
            stats_text += f"Среднее число калорий: {avg_calories:.1f} ккал"
        else:
            stats_text += "\nСредняя продолжительность: 0 мин\n"
            stats_text += "Среднее число калорий: 0 ккал"

        self.stats_label.setText(stats_text)
        # Убрали tight_layout, чтобы вручную управлять позицией
        self.canvas.draw()
    def check_achievements(self):
        # Простая заглушка, так как достижения обновляются в AchievementsWidget
        pass

    def populate_templates(self):
        self.template_selector.clear()
        self.template_selector.addItem("Без шаблона")
        templates = self.db.get_training_templates(self.user["id"])
        for template in templates:
            self.template_selector.addItem(template[1])

    def apply_template(self):
        template_name = self.template_selector.currentText()
        if template_name == "Без шаблона":
            self.exercises.clear()
            self.exercise_list_label.setText("Добавленные упражнения: 0")
            self.duration_input.clear()
            self.type_input.setCurrentIndex(0)
            return

        template = self.db.get_template_by_name(self.user["id"], template_name)
        if not template:
            self.status_label.setText("Ошибка: шаблон не найден")
            return

        # Исправляем распаковку: добавляем все 6 значений
        template_id, user_id, name, training_type, duration, exercises_data = template
        self.exercises.clear()
        for ex in exercises_data:
            exercise = {
                "name": ex[0],  # У `ex` индексы начинаются с 0: name, sets, reps, weight, distance, pace
                "sets": ex[1],
                "reps": ex[2],
                "weight": ex[3],
                "distance": ex[4],
                "pace": ex[5]
            }
            self.exercises.append(exercise)

        self.type_input.setCurrentText(training_type)
        self.duration_input.setText(str(duration))
        self.exercise_list_label.setText(f"Добавленные упражнения: {len(self.exercises)}")
        self.status_label.setText(f"Шаблон '{template_name}' применён")

    def delete_template(self):
        template_name = self.template_selector.currentText()
        if template_name == "Без шаблона":
            self.status_label.setText("Выберите шаблон для удаления")
            return

        reply = QMessageBox.question(
            self, "Подтверждение", f"Вы уверены, что хотите удалить шаблон '{template_name}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.db.delete_template(self.user["id"], template_name)
            self.populate_templates()
            # Очищаем поля после удаления, так как шаблон автоматически применяется
            self.exercises.clear()
            self.exercise_list_label.setText("Добавленные упражнения: 0")
            self.duration_input.clear()
            self.type_input.setCurrentIndex(0)
            self.template_selector.setCurrentText("Без шаблона")
            self.status_label.setText(f"Шаблон '{template_name}' удалён")