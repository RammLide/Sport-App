from PySide6.QtGui import QPalette, QColor

def apply_dark_theme(app):
    palette = QPalette()
    # Темный фон
    palette.setColor(QPalette.Window, QColor(20, 20, 25))  # Почти черный с легким оттенком
    palette.setColor(QPalette.WindowText, QColor(220, 220, 220))  # Светло-серый текст
    palette.setColor(QPalette.Base, QColor(35, 35, 40))  # Темно-серый для полей ввода
    palette.setColor(QPalette.AlternateBase, QColor(45, 45, 50))
    palette.setColor(QPalette.Text, QColor(200, 200, 200))  # Читаемый светлый текст
    palette.setColor(QPalette.Button, QColor(50, 50, 60))  # Темные кнопки
    palette.setColor(QPalette.ButtonText, QColor(220, 220, 220))
    palette.setColor(QPalette.Highlight, QColor(0, 200, 255))  # Мягкий неоновый голубой
    palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))  # Черный текст на выделении
    app.setPalette(palette)

    # Дополнительные стили
    app.setStyleSheet("""
        QWidget {
            font-size: 14px;
            font-family: Arial;
        }
        QPushButton {
            background-color: #32323C;
            border: 1px solid #00C8FF;
            border-radius: 5px;
            padding: 5px;
            color: #DCDCDC;
        }
        QPushButton:hover {
            background-color: #00C8FF;
            color: #000000;
        }
        QLineEdit {
            background-color: #232328;
            border: 1px solid #00C8FF;
            border-radius: 5px;
            padding: 5px;
            color: #C8C8C8;
        }
        QLineEdit:focus {
            border: 2px solid #00C8FF;
        }
        QLabel {
            color: #DCDCDC;
        }
        QTabWidget::pane {
            border: 1px solid #00C8FF;
            background-color: #141419;
        }
        QTabBar::tab {
            background-color: #32323C;
            color: #DCDCDC;
            padding: 5px;
        }
        QTabBar::tab:selected {
            background-color: #00C8FF;
            color: #000000;
        }
    """)