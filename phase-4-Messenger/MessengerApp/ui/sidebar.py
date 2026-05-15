from PySide6.QtWidgets import QFrame, QVBoxLayout, QWidget, QLabel
from PySide6.QtCore import Qt

from utils.avatar import generate_avatar


def build_sidebar(self):
    c = self._theme()

    sidebar = QFrame()
    sidebar.setFixedWidth(72)
    sidebar.setStyleSheet(f"""
        QFrame {{
            background-color: {c["panel_3"]};
            border-right: 1px solid {c["border"]};
        }}
    """)

    layout = QVBoxLayout(sidebar)
    layout.setContentsMargins(10, 20, 10, 20)
    layout.setSpacing(18)
    layout.setAlignment(Qt.AlignTop)

    app_logo = QLabel("💬")
    app_logo.setFixedSize(50, 50)
    app_logo.setAlignment(Qt.AlignCenter)
    app_logo.setStyleSheet("""
        QLabel {
            font-size: 24px;
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 #7B2FF7,
                stop:1 #3A00FF
            );
            border-radius: 15px;
        }
    """)
    layout.addWidget(app_logo, alignment=Qt.AlignHCenter)

    layout.addSpacing(10)

    nav_items = [
        ("🗨️", "Chats", True),
        ("👥", "People", False),
        ("⚙️", "Settings", False),
    ]

    for icon_text, text, active in nav_items:
        nav_card = QWidget()
        nav_card.setFixedWidth(52)

        nav_lay = QVBoxLayout(nav_card)
        nav_lay.setContentsMargins(0, 10, 0, 10)
        nav_lay.setSpacing(5)

        icon = QLabel(icon_text)
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet(
            f"font-size: 22px; color: {'white' if active else c['muted_2']}; background: transparent;"
        )

        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(
            f"font-size: 10px; color: {'white' if active else c['muted_2']}; background: transparent;"
        )

        nav_lay.addWidget(icon)
        nav_lay.addWidget(label)

        if active:
            nav_card.setStyleSheet(f"""
                QWidget {{
                    background-color: {c["card"]};
                    border-radius: 12px;
                }}
            """)

        self.nav_cards.append(nav_card)
        self.nav_icons.append(icon)
        self.nav_labels.append(label)

        layout.addWidget(nav_card, alignment=Qt.AlignHCenter)

    layout.addStretch()

    profile_block = QWidget()
    profile_lay = QVBoxLayout(profile_block)
    profile_lay.setContentsMargins(0, 0, 0, 0)
    profile_lay.setSpacing(6)
    profile_lay.setAlignment(Qt.AlignHCenter)

    profile = QLabel()
    profile.setPixmap(generate_avatar(self.username, 40, is_me=True))
    profile.setFixedSize(40, 40)
    profile.setStyleSheet("background: transparent;")

    self.profile_name_label = QLabel("You")
    self.profile_name_label.setAlignment(Qt.AlignCenter)

    self.profile_status_label = QLabel("Online")
    self.profile_status_label.setAlignment(Qt.AlignCenter)

    profile_lay.addWidget(profile, alignment=Qt.AlignHCenter)
    profile_lay.addWidget(self.profile_name_label)
    profile_lay.addWidget(self.profile_status_label)

    layout.addWidget(profile_block, alignment=Qt.AlignHCenter)
    return sidebar