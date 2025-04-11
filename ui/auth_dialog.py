from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QCheckBox, QLabel, QMessageBox
from database.db_manager import DatabaseManager

class AuthDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.current_user = None
        self.setGeometry(100, 100, 400, 300)
        self.setWindowTitle("Sport Tracker - Вход")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)

        title_label = QLabel("Добро пожаловать в Sport Tracker")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #00C8FF;")
        layout.addWidget(title_label)

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Имя пользователя")
        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.remember_me = QCheckBox("Запомнить меня")
        
        login_btn = QPushButton("Войти")
        register_btn = QPushButton("Зарегистрироваться")
        
        login_btn.clicked.connect(self.login)
        register_btn.clicked.connect(self.register)
        
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.remember_me)
        layout.addWidget(login_btn)
        layout.addWidget(register_btn)
        
        layout.addStretch()
        self.setLayout(layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
        result = cursor.fetchone()
        if result:
            self.current_user = {"id": result[0], "username": username}
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверное имя пользователя или пароль!")

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Введите имя пользователя и пароль!")
            return
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            QMessageBox.warning(self, "Ошибка", "Пользователь с таким именем уже существует!")
        else:
            user_id = self.db.add_user(username, password, self.remember_me.isChecked())
            self.current_user = {"id": user_id, "username": username}
            QMessageBox.information(self, "Успех", "Регистрация прошла успешно!")
            self.accept()