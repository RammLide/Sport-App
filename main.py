import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from ui.auth_dialog import AuthDialog
from ui.styles import apply_dark_theme

if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_dark_theme(app)
    
    auth_dialog = AuthDialog()
    if auth_dialog.exec():
        window = MainWindow(auth_dialog.current_user)
        window.show()
        sys.exit(app.exec())