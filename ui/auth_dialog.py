import json
import os
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QCheckBox, QComboBox, QMessageBox, QTabWidget, QWidget
from database.db_manager import DatabaseManager

class AuthDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.setWindowTitle("Sport Tracker - Авторизация")
        self.setGeometry(200, 200, 400, 500)
        self.current_user = None  # Инициализируем атрибут
        self.init_ui()
        self.load_remembered_user()  # Загружаем сохранённые данные

    def init_ui(self):
        layout = QVBoxLayout()

        # Вкладки: Вход и Регистрация
        self.tabs = QTabWidget()
        self.login_tab = QWidget()
        self.register_tab = QWidget()
        self.tabs.addTab(self.login_tab, "Вход")
        self.tabs.addTab(self.register_tab, "Регистрация")
        layout.addWidget(self.tabs)

        # Вкладка "Вход"
        login_layout = QVBoxLayout()
        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("Имя пользователя")
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Пароль")
        self.login_password.setEchoMode(QLineEdit.Password)
        self.remember_me = QCheckBox("Запомнить меня")
        login_btn = QPushButton("Войти")
        login_btn.clicked.connect(self.login)
        self.login_status = QLabel("")

        login_layout.addWidget(QLabel("Имя пользователя:"))
        login_layout.addWidget(self.login_username)
        login_layout.addWidget(QLabel("Пароль:"))
        login_layout.addWidget(self.login_password)
        login_layout.addWidget(self.remember_me)
        login_layout.addWidget(login_btn)
        login_layout.addWidget(self.login_status)
        login_layout.addStretch()
        self.login_tab.setLayout(login_layout)

        # Вкладка "Регистрация"
        register_layout = QVBoxLayout()
        self.register_username = QLineEdit()
        self.register_username.setPlaceholderText("Имя пользователя")
        self.register_password = QLineEdit()
        self.register_password.setPlaceholderText("Пароль")
        self.register_password.setEchoMode(QLineEdit.Password)
        self.register_confirm_password = QLineEdit()
        self.register_confirm_password.setPlaceholderText("Подтвердите пароль")
        self.register_confirm_password.setEchoMode(QLineEdit.Password)

        # Поля профиля
        self.weight_input = QLineEdit()
        self.weight_input.setPlaceholderText("Вес (кг)")
        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("Рост (см)")
        self.age_input = QLineEdit()
        self.age_input.setPlaceholderText("Возраст (годы)")
        self.gender_input = QComboBox()
        self.gender_input.addItems(["М", "Ж"])

        register_btn = QPushButton("Зарегистрироваться")
        register_btn.clicked.connect(self.register)
        self.register_status = QLabel("")

        register_layout.addWidget(QLabel("Имя пользователя:"))
        register_layout.addWidget(self.register_username)
        register_layout.addWidget(QLabel("Пароль:"))
        register_layout.addWidget(self.register_password)
        register_layout.addWidget(QLabel("Подтвердите пароль:"))
        register_layout.addWidget(self.register_confirm_password)
        register_layout.addWidget(QLabel("Вес (кг):"))
        register_layout.addWidget(self.weight_input)
        register_layout.addWidget(QLabel("Рост (см):"))
        register_layout.addWidget(self.height_input)
        register_layout.addWidget(QLabel("Возраст (годы):"))
        register_layout.addWidget(self.age_input)
        register_layout.addWidget(QLabel("Пол:"))
        register_layout.addWidget(self.gender_input)
        register_layout.addWidget(register_btn)
        register_layout.addWidget(self.register_status)
        register_layout.addStretch()
        self.register_tab.setLayout(register_layout)

        self.setLayout(layout)

    def load_remembered_user(self):
        """Загружает сохранённые данные пользователя из settings.json."""
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", "r") as f:
                    settings = json.load(f)
                    login = settings.get("login", "")
                    password = settings.get("password", "")
                    if login and password:
                        self.login_username.setText(login)
                        self.login_password.setText(password)
                        self.remember_me.setChecked(True)
                        # Пробуем автоматический вход
                        user = self.db.get_user(login, password)
                        if user:
                            self.current_user = {"id": user[0], "username": user[1]}
                            self.login_status.setText("Автоматический вход")
                            self.accept()
        except Exception as e:
            self.login_status.setText(f"Ошибка загрузки: {str(e)}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить данные: {str(e)}")

    def save_remembered_user(self, login, password):
        """Сохраняет логин и пароль, если включён remember_me."""
        if self.remember_me.isChecked():
            settings = {"login": login, "password": password}
            with open("settings.json", "w") as f:
                json.dump(settings, f)
        else:
            if os.path.exists("settings.json"):
                os.remove("settings.json")

    def login(self):
        username = self.login_username.text()
        password = self.login_password.text()
        if not username or not password:
            self.login_status.setText("Заполните все поля")
            QMessageBox.warning(self, "Ошибка", "Заполните имя пользователя и пароль")
            return
        user = self.db.get_user(username, password)
        if user:
            self.save_remembered_user(username, password)
            self.current_user = {"id": user[0], "username": user[1]}
            self.login_status.setText("Успешный вход")
            self.accept()
        else:
            self.login_status.setText("Неверное имя пользователя или пароль")
            QMessageBox.warning(self, "Ошибка", "Неверное имя пользователя или пароль")

    def register(self):
        username = self.register_username.text()
        password = self.register_password.text()
        confirm_password = self.register_confirm_password.text()
        weight = self.weight_input.text()
        height = self.height_input.text()
        age = self.age_input.text()
        gender = self.gender_input.currentText()

        if not username or not password:
            self.register_status.setText("Заполните имя пользователя и пароль")
            QMessageBox.warning(self, "Ошибка", "Заполните имя пользователя и пароль")
            return

        if password != confirm_password:
            self.register_status.setText("Пароли не совпадают")
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают")
            return

        try:
            weight = float(weight) if weight else 0
            height = float(height) if height else 0
            age = int(age) if age else 0
            if weight < 0 or height < 0 or age < 0:
                raise ValueError("Данные профиля не могут быть отрицательными")
        except ValueError as e:
            self.register_status.setText(f"Ошибка: {str(e)}")
            QMessageBox.warning(self, "Ошибка", str(e))
            return

        user_id = self.db.add_user(username, password)
        if user_id:
            if weight > 0 and height > 0 and age > 0:
                self.db.update_user_profile(user_id, weight, height, age, gender)
            self.register_status.setText("Регистрация успешна")
            QMessageBox.information(self, "Успех", "Регистрация успешна!")
            self.current_user = {"id": user_id, "username": username}
            self.accept()
        else:
            self.register_status.setText("Пользователь уже существует")
            QMessageBox.warning(self, "Ошибка", "Пользователь уже существует")