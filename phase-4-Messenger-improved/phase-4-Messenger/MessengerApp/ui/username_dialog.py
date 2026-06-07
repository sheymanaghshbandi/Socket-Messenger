from PySide6.QtWidgets import QWidget, QVBoxLayout, QFrame, QLabel, QLineEdit, QPushButton
from PySide6.QtCore import Qt


class UsernameDialog(QWidget):
    def __init__(self):
        super().__init__()

        self.username = "User"

        self.setWindowTitle("Welcome")
        self.setFixedSize(420, 420)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(20, 20, 20, 20)

        container = QFrame()
        container.setObjectName("container")
        outer_layout.addWidget(container)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(40, 35, 40, 35)
        layout.setSpacing(18)
        layout.setAlignment(Qt.AlignCenter)

        icon = QLabel("💬")
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("font-size: 52px; margin-bottom: 5px;")
        layout.addWidget(icon)

        title = QLabel("Welcome to the Chat")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: white;
        """)
        layout.addWidget(title)

        subtitle = QLabel("Choose your username")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            font-size: 14px;
            color: #B8B8B8;
            margin-bottom: 15px;
        """)
        layout.addWidget(subtitle)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Enter username...")
        self.input.setMinimumHeight(55)

        self.input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255,255,255,0.05);
                border: 2px solid rgba(255,255,255,0.08);
                border-radius: 16px;
                padding-left: 18px;
                color: white;
                font-size: 15px;
            }

            QLineEdit:focus {
                border: 2px solid #7B2FF7;
                background-color: rgba(255,255,255,0.08);
            }
        """)

        self.input.returnPressed.connect(self.accept)

        layout.addWidget(self.input)

        btn = QPushButton("Continue")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setMinimumHeight(55)

        btn.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 18px;
                color: white;
                font-size: 16px;
                font-weight: bold;

                background:qlineargradient(
                    x1:0, y1:0,
                    x2:1, y2:0,
                    stop:0 #7B2FF7,
                    stop:1 #3A00FF
                );
            }

            QPushButton:hover {
                background:qlineargradient(
                    x1:0, y1:0,
                    x2:1, y2:0,
                    stop:0 #8E44FF,
                    stop:1 #4A1DFF
                );
            }
        """)

        btn.clicked.connect(self.accept)

        layout.addWidget(btn)

        self.setStyleSheet("""
            #container {
                background:qlineargradient(
                    x1:0, y1:0,
                    x2:1, y2:1,
                    stop:0 #0F1020,
                    stop:1 #050816
                );

                border-radius: 30px;
                border: 1px solid rgba(255,255,255,0.08);
            }
        """)

    def accept(self):
        text = self.input.text().strip()

        if text:
            self.username = text

        self.close()