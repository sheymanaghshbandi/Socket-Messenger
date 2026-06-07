import random

from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QColor,
    QPixmap,
    QPainter,
    QBrush,
    QPen
)


def generate_avatar(username, size=40, is_me=False):
    if is_me:
        color = QColor("#7B2FF7")
    else:
        random.seed(username)

        colors = [
            "#E74C3C",
            "#3498DB",
            "#2ECC71",
            "#F1C40F",
            "#E67E22",
            "#9B59B6",
            "#1ABC9C"
        ]

        color = QColor(random.choice(colors))

    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)

    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing)

    painter.setBrush(QBrush(color))
    painter.setPen(Qt.NoPen)

    painter.drawEllipse(0, 0, size, size)

    painter.setPen(QPen(Qt.white))

    font = painter.font()
    font.setBold(True)
    font.setPointSize(size // 2 - 2)

    painter.setFont(font)

    letter = username[0].upper() if username else "?"

    painter.drawText(pix.rect(), Qt.AlignCenter, letter)

    painter.end()

    return pix


class AvatarStatusWidget(QWidget):
    def __init__(
        self,
        username,
        avatar_size=36,
        is_me=False,
        online=False,
        show_status=True,
        parent=None,
        border_color="#0E0F14"
    ):
        super().__init__(parent)

        self.username = username
        self.avatar_size = avatar_size
        self.show_status = show_status
        self.online = online
        self.is_me = is_me
        self.border_color = border_color

        total = avatar_size + 10

        self.setFixedSize(total, total)
        self.setAttribute(Qt.WA_StyledBackground, False)

        self.avatar = QLabel(self)

        self.avatar.setPixmap(
            generate_avatar(username, avatar_size, is_me)
        )

        self.avatar.setFixedSize(avatar_size, avatar_size)
        self.avatar.move(0, 0)

        self.avatar.setStyleSheet("""
            background: transparent;
        """)

        self.status_dot = QLabel(self)
        self.status_dot.setFixedSize(12, 12)

        self.status_dot.setStyleSheet(f"""
            QLabel {{
                border: 2px solid {self.border_color};
                border-radius: 6px;
            }}
        """)

        self.status_dot.setVisible(show_status)

        self.set_online(online)

        self._reposition_children()

    def set_online(self, online):
        self.online = online

        if not self.show_status:
            self.status_dot.setVisible(False)
            return

        self.status_dot.setVisible(True)

        self.status_dot.setStyleSheet(f"""
            QLabel {{
                background: {'#22C55E' if online else '#5A5B6A'};
                border: 2px solid {self.border_color};
                border-radius: 6px;
            }}
        """)

    def _reposition_children(self):
        dot_size = self.status_dot.width()

        self.status_dot.move(
            self.avatar_size - dot_size + 2,
            self.avatar_size - dot_size + 2
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)

        self.avatar.move(0, 0)

        self._reposition_children()