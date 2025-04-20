from PySide6.QtGui import QPalette, QColor

def apply_dark_theme(app):
    palette = QPalette()
    # Обновлённая палитра
    palette.setColor(QPalette.Window, QColor(26, 26, 34))  # #1A1A22
    palette.setColor(QPalette.WindowText, QColor(224, 224, 224))  # #E0E0E0
    palette.setColor(QPalette.Base, QColor(40, 40, 50))  # Тёмно-серый для полей ввода
    palette.setColor(QPalette.AlternateBase, QColor(50, 50, 60))
    palette.setColor(QPalette.Text, QColor(224, 224, 224))  # #E0E0E0
    palette.setColor(QPalette.Button, QColor(50, 50, 60))
    palette.setColor(QPalette.ButtonText, QColor(224, 224, 224))
    palette.setColor(QPalette.Highlight, QColor(0, 200, 255))  # #00C8FF
    palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
    app.setPalette(palette)

    # Обновлённые стили (без box-shadow и transition)
    app.setStyleSheet("""
        QWidget {
            font-family: 'Roboto', Arial, sans-serif;
            background-color: #1A1A22;
        }
        QLabel {
            color: #E0E0E0;
        }
        /* Заголовки */
        QLabel[accessibleName="header"] {
            font-size: 18px;
            font-weight: bold;
            color: #FFFFFF;
        }
        /* Мелкий текст */
        QLabel[accessibleName="small"] {
            font-size: 12px;
            color: #A0A0A0;
        }
        QPushButton {
            background-color: #32323C;
            border: 1px solid #00C8FF;
            border-radius: 5px;
            padding: 8px;
            color: #E0E0E0;
            font-size: 14px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #00C8FF, stop:1 #0088CC);
            color: #000000;
        }
        QPushButton[accessibleName="action"] {
            background-color: #FF8C00;
            border: 1px solid #FF8C00;
        }
        QPushButton[accessibleName="action"]:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFA500, stop:1 #FF8C00);
        }
        QLineEdit {
            background-color: #282832;
            border: 1px solid #00C8FF;
            border-radius: 5px;
            padding: 6px;
            color: #E0E0E0;
            font-size: 14px;
        }
        QLineEdit:focus {
            border: 2px solid #00C8FF;
        }
        QComboBox {
            background-color: #282832;
            border: 1px solid #00C8FF;
            border-radius: 5px;
            padding: 6px;
            color: #E0E0E0;
            font-size: 14px;
        }
        QComboBox::drop-down {
            width: 20px;
            border: none;
            background: transparent;
            image: url(icons/dropdown_arrow.svg);  /* Путь к иконке */
        }
        QComboBox::drop-down:hover {
            background: #00C8FF;  /* Цвет при наведении */
        }
        QTabWidget::pane {
            border: 1px solid #00C8FF;
            background-color: #1A1A22;
        }
        QTabBar::tab {
            background-color: #32323C;
            color: #E0E0E0;
            padding: 8px 16px;
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
        }
        QTabBar::tab:selected {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #00C8FF, stop:1 #0088CC);
            color: #000000;
        }
        QTabBar::tab:hover {
            background-color: #00A0E0;
        }
        QListWidget {
            background-color: #282832;
            border: 1px solid #00C8FF;
            border-radius: 5px;
            color: #E0E0E0;
            font-size: 14px;
        }
        QListWidget::item:hover {
            background-color: #00C8FF;
            color: #000000;
        }
        QTextEdit {
            background-color: #282832;
            border: 1px solid #00C8FF;
            border-radius: 5px;
            padding: 6px;
            color: #E0E0E0;
            font-size: 14px;
        }
        QCheckBox {
            color: #E0E0E0;
            font-size: 14px;
        }
        QCalendarWidget {
            background-color: #282832;
            border: 1px solid #00C8FF;
            color: #E0E0E0;
        }
    """)