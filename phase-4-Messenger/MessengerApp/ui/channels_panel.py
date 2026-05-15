from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QListWidget
)
from PySide6.QtCore import Qt


def build_channels_panel(self):
    c = self._theme()

    nav = QFrame()
    nav.setFixedWidth(270)
    nav.setStyleSheet(f"""
        QFrame {{
            background-color: {c["panel"]};
            border-right: 1px solid {c["border"]};
        }}
    """)

    layout = QVBoxLayout(nav)
    layout.setContentsMargins(15, 20, 15, 20)
    layout.setSpacing(0)
    layout.setAlignment(Qt.AlignTop)

    search_row = QHBoxLayout()
    search_row.setSpacing(10)

    search = QLineEdit()
    search.setPlaceholderText("Search chats...")
    search.setFixedHeight(40)
    search.setStyleSheet(f"""
        QLineEdit {{
            background-color: {c["input"]};
            border: 1px solid {c["border"]};
            border-radius: 10px;
            padding-left: 12px;
            color: {c["text"]};
            font-size: 13px;
        }}
        QLineEdit:focus {{
            border: 1px solid #7B2FF7;
        }}
    """)

    new_btn = QPushButton("✎")
    new_btn.setFixedSize(40, 40)
    new_btn.setCursor(Qt.PointingHandCursor)
    new_btn.setStyleSheet(f"""
        QPushButton {{
            border: 1px solid {c["border"]};
            background-color: {c["card_2"]};
            color: {c["text"]};
            border-radius: 10px;
            font-size: 16px;
        }}
        QPushButton:hover {{
            background-color: {c["hover"]};
        }}
    """)

    self.search_input = search
    self.new_btn = new_btn

    search_row.addWidget(search, 1)
    search_row.addWidget(new_btn)
    layout.addLayout(search_row)
    layout.addSpacing(22)

    lbl_chan = QLabel("CHANNELS")
    lbl_chan.setStyleSheet(f"""
        color: {c["muted_2"]};
        font-size: 11px;
        font-weight: bold;
        letter-spacing: 1px;
    """)
    layout.addWidget(lbl_chan)

    self.btn_general = QPushButton("#   General Chat")
    self.btn_general.setCursor(Qt.PointingHandCursor)
    self.btn_general.setFixedHeight(46)
    self._set_general_button_active(True)
    self.btn_general.clicked.connect(self.switch_to_general)
    layout.addWidget(self.btn_general)

    layout.addSpacing(24)

    lbl_dm = QLabel("DIRECT MESSAGES")
    lbl_dm.setStyleSheet(f"""
        color: {c["muted_2"]};
        font-size: 11px;
        font-weight: bold;
        letter-spacing: 1px;
    """)
    layout.addWidget(lbl_dm)

    self.dm_sidebar_list = QListWidget()
    self.dm_sidebar_list.setSpacing(4)
    self.dm_sidebar_list.setStyleSheet(f"""
        QListWidget {{
            background: transparent;
            border: none;
            outline: none;
        }}
        QListWidget::item {{
            background: transparent;
            border-radius: 10px;
            margin-bottom: 2px;
        }}
        QListWidget::item:selected {{
            background: {c["card"]};
        }}
    """)
    self.dm_sidebar_list.itemClicked.connect(self.on_sidebar_dm_clicked)
    self.dm_sidebar_list.itemDoubleClicked.connect(self.on_sidebar_dm_double_clicked)
    layout.addWidget(self.dm_sidebar_list)

    layout.addStretch()
    return nav