# main.py
import sys
from PySide6.QtWidgets import QApplication
from ui.auth_dialog import AuthDialog
from ui.main_window import MainWindow  # Импортируем MainWindow из main_window.py
from ui.styles import apply_dark_theme

if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_dark_theme(app)

    while True:
        auth_dialog = AuthDialog()
        if auth_dialog.exec() and auth_dialog.current_user:
            window = MainWindow(auth_dialog.current_user)
            window.show()
            window.logout_signal.connect(lambda: auth_dialog.show())
            app.exec()
        else:
            break

    sys.exit(0)