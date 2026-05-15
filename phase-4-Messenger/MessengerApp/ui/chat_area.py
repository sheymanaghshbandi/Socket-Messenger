from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QWidget,
    QSizePolicy, QPushButton, QTextEdit
)
from PySide6.QtCore import Qt, QEvent


def build_chat_area(self):
    c = self._theme()

    chat_frame = QFrame()
    chat_frame.setStyleSheet(f"""
        QFrame {{
            background-color: {c["panel_2"]};
        }}
    """)

    layout = QVBoxLayout(chat_frame)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    self.header_frame = QFrame()
    self.header_frame.setFixedHeight(72)
    self.header_frame.setStyleSheet(f"""
        QFrame {{
            background-color: {c["panel_2"]};
            border-bottom: 1px solid {c["border"]};
        }}
    """)

    h_lay = QHBoxLayout(self.header_frame)
    h_lay.setContentsMargins(22, 0, 22, 0)
    h_lay.setSpacing(12)

    self.title_icon = QLabel("#")
    self.title_icon.setAlignment(Qt.AlignCenter)
    self.title_icon.setFixedSize(42, 42)
    self.title_icon.setStyleSheet(f"""
        QLabel {{
            color: #C792FF;
            font-size: 20px;
            font-weight: bold;
            background: {c["card"]};
            border-radius: 21px;
        }}
    """)

    title_box = QVBoxLayout()
    title_box.setSpacing(2)

    self.header_title = QLabel("General Chat")
    self.header_title.setStyleSheet(f"""
        color: {c["text"]};
        font-size: 17px;
        font-weight: bold;
    """)

    self.member_count = QLabel("🟢 0 members online")
    self.member_count.setStyleSheet(f"""
        color: {c["muted"]};
        font-size: 12px;
    """)

    title_box.addWidget(self.header_title)
    title_box.addWidget(self.member_count)

    h_lay.addWidget(self.title_icon)
    h_lay.addLayout(title_box)
    h_lay.addStretch()

    self.theme_toggle_btn = QPushButton()
    self.theme_toggle_btn.setCursor(Qt.PointingHandCursor)
    self.theme_toggle_btn.setMinimumWidth(150)
    self.theme_toggle_btn.setFixedHeight(34)
    self.theme_toggle_btn.clicked.connect(self.toggle_theme)

    self.header_icons = QLabel("🔍   🔔   ⋮")
    self.header_icons.setStyleSheet(f"""
        color: {c["muted"]};
        font-size: 18px;
        letter-spacing: 8px;
        background: transparent;
    """)

    h_lay.addWidget(self.theme_toggle_btn)
    h_lay.addWidget(self.header_icons)

    layout.addWidget(self.header_frame)

    self.scroll = QScrollArea()
    self.scroll.setWidgetResizable(True)
    self.scroll.setStyleSheet("""
        QScrollArea {
            background: transparent;
            border: none;
        }
    """)

    self.chat_area_widget = QWidget()
    self.chat_area_widget.setStyleSheet("background: transparent;")
    self.chat_area_layout = QVBoxLayout(self.chat_area_widget)
    self.chat_area_layout.setAlignment(Qt.AlignTop)
    self.chat_area_layout.setSpacing(16)
    self.chat_area_layout.setContentsMargins(24, 20, 24, 20)

    self.scroll.setWidget(self.chat_area_widget)
    layout.addWidget(self.scroll)

    input_container = QFrame()
    input_container.setStyleSheet("background: transparent;")
    input_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

    input_container_lay = QVBoxLayout(input_container)
    input_container_lay.setContentsMargins(22, 10, 22, 20)

    self.pill_frame = QFrame()
    self.pill_frame.setFixedHeight(56)
    self.pill_frame.setStyleSheet(f"""
        QFrame {{
            background-color: {c["card_2"]};
            border: 1px solid {c["border"]};
            border-radius: 28px;
        }}
    """)

    pill_lay = QHBoxLayout(self.pill_frame)
    pill_lay.setContentsMargins(15, 6, 10, 6)
    pill_lay.setSpacing(8)

    self.btn_attach = QPushButton("+")
    self.btn_attach.setFixedSize(32, 32)
    self.btn_attach.setStyleSheet(f"""
        QPushButton {{
            color: {c["muted"]};
            font-size: 22px;
            font-weight: bold;
            border: none;
            background: transparent;
        }}
        QPushButton:hover {{
            color: {c["text"]};
        }}
    """)

    self.msg_input = QTextEdit()
    self.msg_input.setPlaceholderText("Type your message...")
    self.msg_input.setFixedHeight(34)
    self.msg_input.setStyleSheet(f"""
        QTextEdit {{
            background: transparent;
            border: none;
            color: {c["text"]};
            font-size: 14px;
            padding-top: 6px;
        }}
    """)
    self.msg_input.textChanged.connect(self.dynamic_input_height)
    self.msg_input.installEventFilter(self)

    self.btn_emoji = QPushButton("😊")
    self.btn_emoji.setFixedSize(32, 32)
    self.btn_emoji.setStyleSheet(f"""
        QPushButton {{
            border: none;
            background: transparent;
            font-size: 16px;
            color: {c["text"]};
        }}
    """)

    self.btn_send = QPushButton("➤")
    self.btn_send.setFixedSize(40, 40)
    self.btn_send.setCursor(Qt.PointingHandCursor)
    self.btn_send.setStyleSheet("""
        QPushButton {
            background: #7B2FF7;
            color: white;
            border-radius: 20px;
            font-weight: bold;
            font-size: 16px;
        }
        QPushButton:hover {
            background: #8E44FF;
        }
    """)
    self.btn_send.clicked.connect(self.trigger_send)

    pill_lay.addWidget(self.btn_attach)
    pill_lay.addWidget(self.msg_input, 1)
    pill_lay.addWidget(self.btn_emoji)
    pill_lay.addWidget(self.btn_send)

    input_container_lay.addWidget(self.pill_frame)
    layout.addWidget(input_container)

    return chat_frame