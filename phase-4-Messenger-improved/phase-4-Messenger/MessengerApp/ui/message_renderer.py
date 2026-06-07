from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QWidget
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QFont

from utils.avatar import AvatarStatusWidget


def build_online_users_panel(self):
    c = self._theme()

    panel = QFrame()
    panel.setFixedWidth(300)
    panel.setStyleSheet(f"""
        QFrame {{
            background-color: {c["panel"]};
            border-left: 1px solid {c["border"]};
        }}
    """)

    layout = QVBoxLayout(panel)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    self.user_list = QListWidget()
    self.user_list.setContextMenuPolicy(Qt.CustomContextMenu)
    self.user_list.customContextMenuRequested.connect(self.show_user_context_menu)
    self.user_list.itemDoubleClicked.connect(self.on_user_list_double_click)
    self.user_list.setStyleSheet(f"""
        QListWidget {{
            background-color: transparent;
            border: none;
            padding: 15px;
        }}
        QListWidget::item {{
            background: transparent;
            margin-bottom: 8px;
            border-radius: 10px;
        }}
        QListWidget::item:hover {{
            background-color: {c["hover"]};
        }}
    """)
    layout.addWidget(self.user_list)

    promo_container = QWidget()
    promo_lay = QVBoxLayout(promo_container)
    promo_lay.setContentsMargins(15, 0, 15, 15)

    promo = QFrame()
    promo.setMinimumHeight(130)
    promo.setStyleSheet(f"""
        QFrame {{
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 {c["promo_1"]},
                stop:1 {c["promo_2"]}
            );
            border-radius: 14px;
        }}
    """)

    promo_inner = QVBoxLayout(promo)
    promo_inner.setContentsMargins(20, 18, 20, 18)

    p_title = QLabel("Stay connected")
    p_title.setStyleSheet(f"""
        color: {c["text"]};
        font-weight: bold;
        font-size: 14px;
        background: transparent;
    """)

    p_desc = QLabel("Chat, collaborate and make great things together.")
    p_desc.setWordWrap(True)
    p_desc.setStyleSheet(f"""
        color: {c["muted"]};
        font-size: 12px;
        background: transparent;
    """)

    self.promo_frame = promo
    self.promo_title = p_title
    self.promo_desc = p_desc

    promo_inner.addWidget(p_title)
    promo_inner.addWidget(p_desc)
    promo_inner.addStretch()

    promo_lay.addWidget(promo)
    layout.addWidget(promo_container)

    return panel


def _build_online_row_widget(self, username):
    c = self._theme()
    is_me = (username == self.username)
    display_name = "You" if is_me else username

    row = QFrame()
    row.setMinimumHeight(54)
    row.setStyleSheet(f"""
        QFrame {{
            background: transparent;
            border-radius: 10px;
        }}
        QFrame:hover {{
            background-color: {c["hover"]};
        }}
    """)

    lay = QHBoxLayout(row)
    lay.setContentsMargins(10, 6, 10, 6)
    lay.setSpacing(10)

    avatar = AvatarStatusWidget(
        username,
        avatar_size=36,
        is_me=is_me,
        online=True,
        show_status=True,
        border_color=c["window"]
    )
    avatar.set_online(True)

    text_box = QVBoxLayout()
    text_box.setSpacing(1)

    name_row = QHBoxLayout()
    name_row.setSpacing(6)

    name_lbl = QLabel(display_name)
    name_lbl.setStyleSheet(f"""
        color: {c["text"]};
        font-size: 13px;
        font-weight: bold;
        background: transparent;
    """)

    name_row.addWidget(name_lbl)
    name_row.addStretch()

    status_row = QHBoxLayout()
    status_row.setSpacing(5)

    status_lbl = QLabel("Online")
    status_lbl.setStyleSheet(f"""
        color: {c["muted"]};
        font-size: 11px;
        background: transparent;
    """)

    status_row.addWidget(status_lbl)
    status_row.addStretch()

    text_box.addLayout(name_row)
    text_box.addLayout(status_row)

    lay.addWidget(avatar)
    lay.addLayout(text_box, 1)

    return row