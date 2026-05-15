from PySide6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QListWidget,
    QPushButton, QTextEdit, QScrollArea, QLabel, QFrame,
    QSizePolicy, QMenu, QLineEdit, QListWidgetItem, QGraphicsDropShadowEffect,
    QStackedWidget, QFileDialog, QDialog, QGridLayout
)
from PySide6.QtCore import Qt, Signal, QObject, QDateTime, QEvent, QSize, QMargins, QRect, QPoint
from PySide6.QtGui import QColor, QPalette, QIcon, QTextDocument, QPixmap, QPainter, QBrush, QPen, QFont
import random
import hashlib
import base64
import json
from client import ClientNetwork


# ============================================================
#                       USERNAME DIALOG
# ============================================================
class UsernameDialog(QWidget):
    def __init__(self):
        super().__init__()
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
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        layout.addWidget(title)

        subtitle = QLabel("Choose your username")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 14px; color: #B8B8B8; margin-bottom: 15px;")
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
                background:qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7B2FF7, stop:1 #3A00FF);
            }
            QPushButton:hover {
                background:qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8E44FF, stop:1 #4A1DFF);
            }
        """)
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)

        self.setStyleSheet("""
            #container {
                background:qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0F1020, stop:1 #050816);
                border-radius: 30px;
                border: 1px solid rgba(255,255,255,0.08);
            }
        """)

    def accept(self):
        self.username = self.input.text().strip() if self.input.text().strip() else "User"
        self.close()


# ============================================================
#                   AVATAR UTILITY
# ============================================================
def generate_avatar(username, size=40, is_me=False):
    if is_me:
        color = QColor("#7B2FF7")
    else:
        random.seed(username)
        colors = ["#E74C3C", "#3498DB", "#2ECC71", "#F1C40F", "#E67E22", "#9B59B6", "#1ABC9C"]
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
    def __init__(self, username, avatar_size=36, is_me=False, online=False, show_status=True, parent=None, border_color="#0E0F14"):
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
        self.avatar.setPixmap(generate_avatar(username, avatar_size, is_me))
        self.avatar.setFixedSize(avatar_size, avatar_size)
        self.avatar.move(0, 0)
        self.avatar.setStyleSheet("background: transparent;")

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
        self.status_dot.move(self.avatar_size - dot_size + 2, self.avatar_size - dot_size + 2)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.avatar.move(0, 0)
        self._reposition_children()


class ClickableLabel(QLabel):
    clicked = Signal()

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


class ImagePreviewDialog(QDialog):
    def __init__(self, pixmap, title="Picture", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(520, 380)
        self.resize(920, 700)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 180);")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(18, 18, 18, 18)

        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #0B1020;
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 18px;
            }
        """)
        frame_lay = QVBoxLayout(frame)
        frame_lay.setContentsMargins(16, 16, 16, 16)
        frame_lay.setSpacing(12)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: white; font-size: 14px; font-weight: bold; background: transparent;")

        self.image_lbl = QLabel()
        self.image_lbl.setAlignment(Qt.AlignCenter)
        self.image_lbl.setStyleSheet("background: transparent;")
        self._pixmap = pixmap
        self._apply_pixmap()

        frame_lay.addWidget(title_lbl)
        frame_lay.addWidget(self.image_lbl, 1)
        outer.addWidget(frame)

    def _apply_pixmap(self):
        if self._pixmap is None or self._pixmap.isNull():
            return
        scaled = self._pixmap.scaled(self.size() - QSize(70, 110), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_lbl.setPixmap(scaled)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_pixmap()




class EmojiPickerDialog(QDialog):
    emoji_selected = Signal(str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(330, 330)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #0B1020;
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 18px;
            }
        """)
        outer.addWidget(frame)

        grid = QGridLayout(frame)
        grid.setContentsMargins(12, 12, 12, 12)
        grid.setSpacing(6)


        emojis = [
            "😀", "😃", "😄", "😁", "😊",
            "🙂", "😍", "🥰", "😘", "🤗",
            "😂", "🤣", "😉", "😎", "😭",
            "😡", "👍", "👎", "🙏", "🎉",
            "❤️", "🔥", "✨", "💯", "✅",
            "📷", "📸", "🖼️", "🌟", "💬",
        ]

        cols = 5
        for index, emoji in enumerate(emojis):
            row = index // cols
            col = index % cols
            btn = QPushButton(emoji)
            btn.setFixedSize(48, 48)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    border-radius: 12px;
                    background: rgba(255,255,255,0.03);
                    font-size: 22px;
                }
                QPushButton:hover {
                    background: rgba(123, 47, 247, 0.22);
                }
            """)
            btn.clicked.connect(lambda checked=False, e=emoji: self._choose_emoji(e))
            grid.addWidget(btn, row, col)

    def _choose_emoji(self, emoji):
        self.emoji_selected.emit(emoji)
        self.accept()

# ============================================================
#                         CHAT WINDOW
# ============================================================
class ChatWindow(QWidget):
    MEDIA_PREFIX = "__CHAT_MEDIA__:"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Messenger")
        self.resize(1260, 780)

        self.theme = "dark"
        self.theme_toggle_btn = None
        self.profile_name_label = None
        self.profile_status_label = None
        self.header_frame = None
        self.title_icon = None
        self.search_input = None
        self.new_btn = None
        self.header_icons = None
        self.nav_cards = []
        self.nav_icons = []
        self.nav_labels = []
        self.promo_frame = None
        self.promo_title = None
        self.promo_desc = None
        self.btn_attach = None
        self.btn_emoji = None
        self.btn_send = None

        # --------------------------------------------------------
        # USERNAME SELECTION
        # --------------------------------------------------------
        dialog = UsernameDialog()
        dialog.show()
        while dialog.isVisible():
            QApplication.processEvents()

        self.username = dialog.username

        # --------------------------------------------------------
        # APPLICATION STATE
        # --------------------------------------------------------
        self.active_chat_target = None
        self.current_users = []
        self._previous_users_snapshot = set()
        self._seen_initial_users = False

        self.messages_store = {"General": []}
        self.message_widgets = {}
        self.editing_msg_id = None
        self.editing_bubble = None
        self.dm_row_items = {}
        self.user_row_items = {}

        # --------------------------------------------------------
        # UI
        # --------------------------------------------------------
        self.init_ui()

        # --------------------------------------------------------
        # NETWORK
        # --------------------------------------------------------
        self.client = ClientNetwork(username=self.username)
        self.client.system_message.connect(self.append_system_message)
        self.client.users_update.connect(self.update_users_list)
        self.client.history_received.connect(self.handle_history)
        self.client.message_received.connect(self.handle_public_incoming)
        self.client.private_message_received.connect(self.handle_private_incoming)
        self.client.message_edited.connect(self.handle_remote_edit)
        self.client.connect()

        self.apply_theme("dark")

    # ============================================================
    #                        UI BOOTSTRAP
    # ============================================================
    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.sidebar = self.column_1_sidebar()
        self.nav_panel = self.column_2_navigation()
        self.chat_panel = self.column_3_chat_area()
        self.user_panel = self.column_4_user_list()

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.nav_panel)
        main_layout.addWidget(self.chat_panel)
        main_layout.addWidget(self.user_panel)

    def _theme(self):
        dark = self.theme == "dark"
        return {
            "window": "#070B14" if dark else "#F7F8FF",
            "panel": "#0A1020" if dark else "#FFFFFF",
            "panel_2": "#0D1527" if dark else "#FBFCFF",
            "panel_3": "#080D1A" if dark else "#F8F6FF",
            "card": "#16213A" if dark else "#EEF0FF",
            "card_2": "#10192B" if dark else "#FFFFFF",
            "border": "#23324D" if dark else "#DCE3F0",
            "text": "#F8FAFC" if dark else "#101828",
            "muted": "#A7B2C5" if dark else "#5E6B7E",
            "muted_2": "#71819B" if dark else "#8C97AB",
            "input": "#0F172A" if dark else "#FFFFFF",
            "hover": "#17253D" if dark else "#EAF0FF",
            "bubble_other": "#162235" if dark else "#FBF9FF",
            "promo_1": "#0E1730" if dark else "#F6F0FF",
            "promo_2": "#09101F" if dark else "#EEF4FF",
            "accent": "#7B2FF7",
            "accent_2": "#4A1DFF",
        }


    def apply_theme(self, theme):
        self.theme = theme
        c = self._theme()

        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(c["window"]))
        palette.setColor(QPalette.Base, QColor(c["window"]))
        palette.setColor(QPalette.Text, QColor(c["text"]))
        self.setPalette(palette)

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {c["window"]};
                color: {c["text"]};
                font-family: "Segoe UI", Arial, sans-serif;
            }}
            QScrollBar:vertical {{
                border: none;
                background: transparent;
                width: 8px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {c["border"]};
                min-height: 20px;
                border-radius: 4px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)

        if hasattr(self, "sidebar") and self.sidebar is not None:
            self.sidebar.setStyleSheet(f"""
                QFrame {{
                    background-color: {c["panel_3"]};
                    border-right: 1px solid {c["border"]};
                }}
            """)

        if hasattr(self, "nav_panel") and self.nav_panel is not None:
            self.nav_panel.setStyleSheet(f"""
                QFrame {{
                    background-color: {c["panel"]};
                    border-right: 1px solid {c["border"]};
                }}
            """)

        if hasattr(self, "chat_panel") and self.chat_panel is not None:
            if self.theme == "dark":
                self.chat_panel.setStyleSheet("""
                    QFrame {
                        background: qlineargradient(
                            x1:0, y1:0, x2:1, y2:1,
                            stop:0 #07101F,
                            stop:0.5 #0B1430,
                            stop:1 #050814
                        );
                    }
                """)
            else:
                self.chat_panel.setStyleSheet("""
                    QFrame {
                        background: qlineargradient(
                            x1:0, y1:0, x2:1, y2:1,
                            stop:0 #FEFEFF,
                            stop:0.5 #F6F0FF,
                            stop:1 #EEF4FF
                        );
                    }
                """)

        if hasattr(self, "user_panel") and self.user_panel is not None:
            self.user_panel.setStyleSheet(f"""
                QFrame {{
                    background-color: {c["panel"]};
                    border-left: 1px solid {c["border"]};
                }}
            """)

        if self.header_frame is not None:
            self.header_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {c["panel_2"]};
                    border-bottom: 1px solid {c["border"]};
                }}
            """)

        if self.title_icon is not None:
            self.title_icon.setStyleSheet(f"""
                QLabel {{
                    color: #C792FF;
                    font-size: 20px;
                    font-weight: bold;
                    background: {c["card"]};
                    border-radius: 21px;
                }}
            """)

        if hasattr(self, "header_title"):
            self.header_title.setStyleSheet(f"""
                color: {c["text"]};
                font-size: 17px;
                font-weight: bold;
            """)

        if hasattr(self, "member_count"):
            self.member_count.setStyleSheet(f"""
                color: {c["muted"]};
                font-size: 12px;
            """)

        if hasattr(self, "pill_frame"):
            self.pill_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {c["card_2"]};
                    border: 1px solid {c["border"]};
                    border-radius: 28px;
                }}
            """)

        if hasattr(self, "msg_input"):
            self.msg_input.setStyleSheet(f"""
                QTextEdit {{
                    background: transparent;
                    border: none;
                    color: {c["text"]};
                    font-size: 14px;
                    padding-top: 6px;
                }}
            """)

        if hasattr(self, "btn_general"):
            self._set_general_button_active(self.active_chat_target is None)

        if hasattr(self, "dm_sidebar_list"):
            self.dm_sidebar_list.setStyleSheet(f"""
                QListWidget {{
                    background: transparent;
                    border: none;
                    outline: none;
                }}
                QListWidget::item {{
                    background: transparent;
                    border-radius: 12px;
                    margin-bottom: 2px;
                }}
                QListWidget::item:selected {{
                    background: {c["card"]};
                }}
            """)

        if hasattr(self, "user_list"):
            self.user_list.setStyleSheet(f"""
                QListWidget {{
                    background-color: transparent;
                    border: none;
                    padding: 15px;
                }}
                QListWidget::item {{
                    background: transparent;
                    margin-bottom: 8px;
                    border-radius: 12px;
                }}
                QListWidget::item:hover {{
                    background-color: {c["hover"]};
                }}
            """)

        if self.theme_toggle_btn is not None:
            self.theme_toggle_btn.setText("Light mode ☀️" if self.theme == "dark" else "Dark mode 🌙")
            self.theme_toggle_btn.setStyleSheet(f"""
                QPushButton {{
                    border: 1px solid {c["border"]};
                    background: {c["card_2"]};
                    color: {c["text"]};
                    border-radius: 18px;
                    padding: 8px 14px;
                    font-size: 12px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background: {c["hover"]};
                    border-color: {c["muted_2"]};
                }}
            """)

        if self.search_input is not None:
            self.search_input.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {c["input"]};
                    border: 1px solid {c["border"]};
                    border-radius: 12px;
                    padding-left: 12px;
                    color: {c["text"]};
                    font-size: 13px;
                }}
                QLineEdit:focus {{
                    border: 1px solid {c["accent"]};
                }}
            """)

        if self.new_btn is not None:
            self.new_btn.setStyleSheet(f"""
                QPushButton {{
                    border: 1px solid {c["border"]};
                    background-color: {c["card_2"]};
                    color: {c["text"]};
                    border-radius: 12px;
                    font-size: 16px;
                }}
                QPushButton:hover {{
                    background-color: {c["hover"]};
                }}
            """)

        if self.header_icons is not None:
            self.header_icons.setStyleSheet(f"""
                color: {c["muted"]};
                font-size: 18px;
                letter-spacing: 8px;
                background: transparent;
            """)

        for idx, (card, icon, label) in enumerate(zip(self.nav_cards, self.nav_icons, self.nav_labels)):
            active = (idx == 0)
            if active:
                card.setStyleSheet(f"""
                    QWidget {{
                        background-color: {c["card"]};
                        border-radius: 12px;
                    }}
                """)
            else:
                card.setStyleSheet("QWidget { background: transparent; border-radius: 12px; }")

            icon.setStyleSheet(
                f"font-size: 22px; color: {'white' if active else c['muted_2']}; background: transparent;"
            )
            label.setStyleSheet(
                f"font-size: 10px; color: {'white' if active else c['muted_2']}; background: transparent;"
            )

        if self.btn_attach is not None:
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

        if self.btn_emoji is not None:
            self.btn_emoji.setStyleSheet(f"""
                QPushButton {{
                    border: none;
                    background: transparent;
                    font-size: 16px;
                    color: {c["text"]};
                }}
            """)

        if self.btn_send is not None:
            self.btn_send.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:1,
                        stop:0 {c["accent"]},
                        stop:1 {c["accent_2"]}
                    );
                    color: white;
                    border-radius: 20px;
                    font-weight: bold;
                    font-size: 16px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:1,
                        stop:0 #8E44FF,
                        stop:1 #4A1DFF
                    );
                }}
            """)

        if self.promo_frame is not None:
            self.promo_frame.setStyleSheet(f"""
                QFrame {{
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:1,
                        stop:0 {c["promo_1"]},
                        stop:1 {c["promo_2"]}
                    );
                    border-radius: 14px;
                }}
            """)

        if self.promo_title is not None:
            self.promo_title.setStyleSheet(f"""
                color: {c["text"]};
                font-weight: bold;
                font-size: 14px;
                background: transparent;
            """)

        if self.promo_desc is not None:
            self.promo_desc.setStyleSheet(f"""
                color: {c["muted"]};
                font-size: 12px;
                background: transparent;
            """)

        if self.profile_name_label is not None:
            self.profile_name_label.setStyleSheet(f"""
                color: {c["text"]};
                font-size: 11px;
                font-weight: bold;
                background: transparent;
            """)

        if self.profile_status_label is not None:
            self.profile_status_label.setStyleSheet(f"""
                color: {c["muted"]};
                font-size: 10px;
                background: transparent;
            """)

        self.refresh_ui_chat()
        self.refresh_direct_messages_list()
        self.update_users_list(self.current_users)

    def toggle_theme(self):
        self.apply_theme("light" if self.theme == "dark" else "dark")

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()
            if widget is not None:
                widget.deleteLater()
            elif child_layout is not None:
                self.clear_layout(child_layout)

    def scroll_chat_to_bottom(self):
        QApplication.processEvents()
        if hasattr(self, "scroll"):
            scrollbar = self.scroll.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    def current_chat_key(self):
        return "General" if self.active_chat_target is None else self.active_chat_target

    def _stable_private_message_id(self, sender, receiver, timestamp, content):
        payload = f"{sender}|{receiver}|{timestamp}|{content}"
        digest = hashlib.sha1(payload.encode("utf-8")).hexdigest()
        return f"pm:{digest[:20]}"

    def _extract_message_args(self, args, expected_names):
        values = list(args)
        if len(values) == len(expected_names):
            return values
        return values[:len(expected_names)]

    # ============================================================
    #                   COLUMN 1: SLIM SIDEBAR
    # ============================================================
    def column_1_sidebar(self):
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

    # ============================================================
    #                COLUMN 2: CHANNELS + DIRECT MESSAGES
    # ============================================================
    def column_2_navigation(self):
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
                border-radius: 12px;
                padding-left: 12px;
                color: {c["text"]};
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 1px solid {c["accent"]};
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
                border-radius: 12px;
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

    # ============================================================
    #                     COLUMN 3: CHAT AREA
    # ============================================================
    def column_3_chat_area(self):
        c = self._theme()
        chat_frame = QFrame()
        if self.theme == "dark":
            chat_frame.setStyleSheet("""
                QFrame {
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:1,
                        stop:0 #07101F,
                        stop:0.5 #0B1430,
                        stop:1 #050814
                    );
                }
            """)
        else:
            chat_frame.setStyleSheet("""
                QFrame {
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:1,
                        stop:0 #FEFEFF,
                        stop:0.5 #F6F0FF,
                        stop:1 #EEF4FF
                    );
                }
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

        header_icons = QLabel("🔍   🔔   ⋮")
        header_icons.setStyleSheet(f"""
            color: {c["muted"]};
            font-size: 18px;
            letter-spacing: 8px;
        """)
        self.header_icons = header_icons

        h_lay.addWidget(self.theme_toggle_btn)
        h_lay.addWidget(header_icons)

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
                border-radius: 30px;
            }}
        """)

        pill_lay = QHBoxLayout(self.pill_frame)
        pill_lay.setContentsMargins(15, 6, 10, 6)
        pill_lay.setSpacing(8)

        btn_attach = QPushButton("+")
        btn_attach.setFixedSize(32, 32)
        btn_attach.setCursor(Qt.PointingHandCursor)
        btn_attach.clicked.connect(self.pick_and_send_image)
        btn_attach.setStyleSheet(f"""
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

        btn_emoji = QPushButton("😊")
        btn_emoji.setFixedSize(32, 32)
        btn_emoji.setCursor(Qt.PointingHandCursor)
        btn_emoji.clicked.connect(self.open_emoji_picker)
        btn_emoji.setStyleSheet(f"""
            QPushButton {{
                border: none;
                background: transparent;
                font-size: 16px;
                color: {c["text"]};
            }}
        """)

        btn_send = QPushButton("➤")
        btn_send.setFixedSize(40, 40)
        btn_send.setCursor(Qt.PointingHandCursor)
        btn_send.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {c["accent"]},
                    stop:1 {c["accent_2"]}
                );
                color: white;
                border-radius: 20px;
                font-weight: bold;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #8E44FF,
                    stop:1 #4A1DFF
                );
            }}
        """)
        btn_send.clicked.connect(self.trigger_send)

        self.btn_attach = btn_attach
        self.btn_emoji = btn_emoji
        self.btn_send = btn_send

        pill_lay.addWidget(btn_attach)
        pill_lay.addWidget(self.msg_input, 1)
        pill_lay.addWidget(btn_emoji)
        pill_lay.addWidget(btn_send)

        input_container_lay.addWidget(self.pill_frame)
        layout.addWidget(input_container)

        return chat_frame

    # ============================================================
    #                    COLUMN 4: ONLINE USERS
    # ============================================================
    def column_4_user_list(self):
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
                border-radius: 12px;
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
                border-radius: 16px;
                border: 1px solid {c["border"]};
            }}
        """)

        promo_shadow = QGraphicsDropShadowEffect(promo)
        promo_shadow.setBlurRadius(28)
        promo_shadow.setOffset(0, 10)
        promo_shadow.setColor(QColor(12, 18, 34, 90 if self.theme == "dark" else 28))
        promo.setGraphicsEffect(promo_shadow)

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

    def _is_media_payload(self, content):
        return isinstance(content, str) and content.startswith(self.MEDIA_PREFIX)

    def _encode_image_payload(self, image_path, caption=""):
        with open(image_path, "rb") as f:
            raw = f.read()
        payload = {
            "kind": "image",
            "filename": image_path.split("/")[-1],
            "caption": caption or "",
            "data": base64.b64encode(raw).decode("ascii"),
        }
        return self.MEDIA_PREFIX + json.dumps(payload, ensure_ascii=False)

    def _decode_message_payload(self, content):
        if not self._is_media_payload(content):
            return {"kind": "text", "text": content, "caption": "", "filename": None, "image_bytes": None}

        try:
            payload = json.loads(content[len(self.MEDIA_PREFIX):])
            raw = base64.b64decode(payload.get("data", ""))
            return {
                "kind": payload.get("kind", "image"),
                "text": payload.get("caption", ""),
                "caption": payload.get("caption", ""),
                "filename": payload.get("filename"),
                "image_bytes": raw,
            }
        except Exception:
            return {"kind": "text", "text": content, "caption": "", "filename": None, "image_bytes": None}

    def _pixmap_from_bytes(self, raw_bytes):
        pix = QPixmap()
        if raw_bytes:
            pix.loadFromData(raw_bytes)
        return pix

    def _open_image_preview(self, pixmap, title):
        if pixmap is None or pixmap.isNull():
            return
        dialog = ImagePreviewDialog(pixmap, title=title, parent=self)
        dialog.exec()

    def _open_emoji_menu(self, button):
        dialog = EmojiPickerDialog(self)
        dialog.emoji_selected.connect(self._insert_emoji)

        dialog.adjustSize()
        popup_size = dialog.sizeHint()
        if popup_size.isEmpty():
            popup_size = dialog.size()

        button_top_left = button.mapToGlobal(QPoint(0, 0))
        button_bottom_left = button.mapToGlobal(button.rect().bottomLeft())

        screen = button.screen() or QApplication.primaryScreen()
        available = screen.availableGeometry()

        margin = 8

        x = button_top_left.x() + (button.width() - popup_size.width()) // 2

        below_y = button_bottom_left.y() + margin
        above_y = button_top_left.y() - popup_size.height() - margin

        if below_y + popup_size.height() <= available.bottom():
            y = below_y
        else:
            y = above_y

        if x < available.left() + margin:
            x = available.left() + margin
        if x + popup_size.width() > available.right() - margin:
            x = available.right() - popup_size.width() - margin

        if y < available.top() + margin:
            y = available.top() + margin
        if y + popup_size.height() > available.bottom() - margin:
            y = available.bottom() - popup_size.height() - margin

        dialog.move(x, y)
        dialog.exec()

    def _insert_emoji(self, emoji):
        self.msg_input.insertPlainText(emoji)
        self.msg_input.setFocus()

    def open_emoji_picker(self):
        self._open_emoji_menu(self.btn_emoji)

    def pick_and_send_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select picture",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp)"
        )
        if not file_path:
            return

        caption = self.msg_input.toPlainText().strip()
        payload = self._encode_image_payload(file_path, caption=caption)

        if self.active_chat_target is None:
            self.client.send_message(payload)
        else:
            self.client.send_private_message(self.active_chat_target, payload)

        self.msg_input.clear()
        self.msg_input.setFixedHeight(34)
        self.msg_input.setFocus()

    # ============================================================
    #                        DATA HELPERS
    # ============================================================
    def _create_message_record(self, msg_id, sender, content, timestamp, edited=False, **extra):
        record = {
            "id": msg_id,
            "sender": sender,
            "content": content,
            "timestamp": timestamp,
            "edited": edited,
        }
        record.update(extra)
        return record

    def _store_message(self, chat_key, record):
        if chat_key not in self.messages_store:
            self.messages_store[chat_key] = []

        record_id = record.get("id")
        if record_id is not None:
            for existing in self.messages_store[chat_key]:
                if existing.get("id") == record_id:
                    return

        self.messages_store[chat_key].append(record)

    def _get_preview_text(self, username):
        history = self.messages_store.get(username, [])
        if not history:
            return "Online" if username in self.current_users else "No messages yet"

        last = history[-1]
        parsed = self._decode_message_payload(last["content"])
        if parsed["kind"] == "image":
            content = "[Photo]" + (f" {parsed['caption']}" if parsed["caption"] else "")
        else:
            content = last["content"].replace("\n", " ").strip()
            if len(content) > 24:
                content = content[:24] + "..."

        if last["sender"] == self.username:
            return f"You: {content}"
        return content

    def _all_dm_targets(self):
        targets = set(self.messages_store.keys())
        targets.discard("General")
        targets.discard(self.username)
        return sorted(
            targets,
            key=lambda u: (
                u not in self.current_users,
                u.lower()
            )
        )

    def _set_general_button_active(self, active):
        c = self._theme()
        if active:
            self.btn_general.setStyleSheet(f"""
                QPushButton {{
                    text-align: left;
                    padding-left: 15px;
                    background: {c["card"]};
                    border-radius: 12px;
                    font-weight: bold;
                    border: 1px solid {c["border"]};
                    color: {c["text"]};
                }}
                QPushButton:hover {{
                    background: {c["hover"]};
                }}
            """)
        else:
            self.btn_general.setStyleSheet(f"""
                QPushButton {{
                    text-align: left;
                    padding-left: 15px;
                    background: transparent;
                    border-radius: 12px;
                    border: none;
                    color: {c["text"]};
                }}
                QPushButton:hover {{
                    background: {c["hover"]};
                }}
            """)

    # ============================================================
    #                 DIRECT MESSAGES LIST MANAGEMENT
    # ============================================================
    def refresh_direct_messages_list(self):
        current_target = self.active_chat_target
        self.dm_sidebar_list.clear()
        self.dm_row_items.clear()

        for username in self._all_dm_targets():
            item = QListWidgetItem()
            item.setData(Qt.UserRole, username)
            item.setSizeHint(QSize(220, 64))

            row = self._build_dm_row_widget(username, active=(username == current_target))
            self.dm_sidebar_list.addItem(item)
            self.dm_sidebar_list.setItemWidget(item, row)
            self.dm_row_items[username] = item

    def _build_dm_row_widget(self, username, active=False):
        c = self._theme()
        is_online = username in self.current_users
        preview_text = self._get_preview_text(username)
        display_name = "You" if username == self.username else username

        row = QFrame()
        row.setMinimumHeight(58)
        row.setStyleSheet(self._dm_row_stylesheet(active))

        lay = QHBoxLayout(row)
        lay.setContentsMargins(10, 8, 10, 8)
        lay.setSpacing(10)

        avatar = AvatarStatusWidget(username, avatar_size=36, is_me=(username == self.username), online=is_online, show_status=True, border_color=c["window"])
        avatar.set_online(is_online)

        text_box = QVBoxLayout()
        text_box.setSpacing(1)

        name_lbl = QLabel(display_name)
        name_lbl.setStyleSheet(f"""
            color: {c["text"]};
            font-size: 13px;
            font-weight: bold;
            background: transparent;
        """)

        preview_lbl = QLabel(preview_text)
        preview_lbl.setStyleSheet(f"""
            color: {c["muted"]};
            font-size: 11px;
            background: transparent;
        """)

        text_box.addWidget(name_lbl)
        text_box.addWidget(preview_lbl)

        right_box = QVBoxLayout()
        right_box.setSpacing(2)
        right_box.setAlignment(Qt.AlignCenter)

        status = QLabel("Online" if is_online else "Offline")
        status.setStyleSheet(f"""
            color: {c["muted"]};
            font-size: 10px;
            background: transparent;
        """)

        right_box.addWidget(status, alignment=Qt.AlignHCenter)

        lay.addWidget(avatar)
        lay.addLayout(text_box, 1)
        lay.addLayout(right_box)

        return row

    def _dm_row_stylesheet(self, active=False):
        c = self._theme()
        if active:
            return f"""
                QFrame {{
                    background-color: {c["card"]};
                    border-radius: 10px;
                }}
                QFrame:hover {{
                    background-color: {c["hover"]};
                }}
            """
        return f"""
            QFrame {{
                background: transparent;
                border-radius: 12px;
            }}
            QFrame:hover {{
                background-color: {c["hover"]};
            }}
        """

    # ============================================================
    #                 ONLINE USERS LIST MANAGEMENT
    # ============================================================
    def update_users_list(self, users):
        c = self._theme()
        new_users = list(users)
        new_user_set = set(new_users)

        if self._seen_initial_users:
            pass
        else:
            self._seen_initial_users = True

        self._previous_users_snapshot = new_user_set
        self.current_users = new_users
        self.user_list.clear()

        self.member_count.setText(f"🟢 {len(users)} members online")
        self.refresh_direct_messages_list()

        header = QListWidgetItem(f"ONLINE — {len(users)}")
        header.setFlags(header.flags() & ~Qt.ItemIsSelectable)
        header.setForeground(QColor(c["muted_2"]))
        header.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.user_list.addItem(header)

        sorted_users = sorted(users, key=lambda u: (u != self.username, u.lower()))

        for u in sorted_users:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, u)
            item.setSizeHint(QSize(220, 60))

            row = self._build_online_row_widget(u)
            self.user_list.addItem(item)
            self.user_list.setItemWidget(item, row)
            self.user_row_items[u] = item

    def _build_online_row_widget(self, username):
        c = self._theme()
        is_me = (username == self.username)
        display_name = "You" if is_me else username

        row = QFrame()
        row.setMinimumHeight(54)
        row.setStyleSheet(f"""
            QFrame {{
                background: transparent;
                border-radius: 12px;
            }}
            QFrame:hover {{
                background-color: {c["hover"]};
            }}
        """)

        lay = QHBoxLayout(row)
        lay.setContentsMargins(10, 6, 10, 6)
        lay.setSpacing(10)

        avatar = AvatarStatusWidget(username, avatar_size=36, is_me=is_me, online=True, show_status=True, border_color=c["window"])
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

    def show_user_context_menu(self, pos):
        c = self._theme()
        item = self.user_list.itemAt(pos)
        if item is None:
            return

        username = item.data(Qt.UserRole)
        if not username:
            return

        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {c["card_2"]};
                color: {c["text"]};
                border: 1px solid {c["border"]};
            }}
            QMenu::item:selected {{
                background-color: {c["accent"]};
            }}
        """)

        send_action = menu.addAction("Send Message")
        copy_action = menu.addAction("Copy Username")

        action = menu.exec_(self.user_list.viewport().mapToGlobal(pos))
        if action == send_action:
            self.open_private_chat(username)
        elif action == copy_action:
            QApplication.clipboard().setText(username)

    # ============================================================
    #                  CHAT SWITCHING / NAVIGATION
    # ============================================================
    def switch_to_general(self):
        self.active_chat_target = None
        self.header_title.setText("General Chat")
        self._set_general_button_active(True)
        self.refresh_direct_messages_list()
        self.refresh_ui_chat()

    def open_private_chat(self, username):
        if username == self.username:
            return

        self.active_chat_target = username
        self.header_title.setText(username)
        self._set_general_button_active(False)

        if username not in self.messages_store:
            self.messages_store[username] = []

        self.refresh_direct_messages_list()
        self.refresh_ui_chat()
        self.msg_input.setFocus()

        if username in self.dm_row_items:
            item = self.dm_row_items[username]
            self.dm_sidebar_list.setCurrentItem(item)

    def on_sidebar_dm_clicked(self, item):
        username = item.data(Qt.UserRole)
        if username:
            self.open_private_chat(username)

    def on_sidebar_dm_double_clicked(self, item):
        username = item.data(Qt.UserRole)
        if username:
            self.open_private_chat(username)

    def on_user_list_double_click(self, item):
        username = item.data(Qt.UserRole)
        if username and username != self.username:
            self.open_private_chat(username)

    # ============================================================
    #                      MESSAGE RENDERING
    # ============================================================
    def refresh_ui_chat(self):
        self.clear_layout(self.chat_area_layout)
        self.message_widgets.clear()

        history = self.messages_store.get(self.current_chat_key(), [])
        for record in history:
            if record.get("system"):
                self.draw_system_message(record["content"])
            else:
                self.draw_bubble(record)

        self.scroll_chat_to_bottom()

    def handle_history(self, messages):
        if not isinstance(messages, list) or not messages:
            return

        for entry in messages:
            if not isinstance(entry, dict):
                continue

            msg_type = str(entry.get("msg_type") or entry.get("type") or "public").lower()
            sender = entry.get("sender") or entry.get("sender_username") or "Unknown"
            receiver = entry.get("receiver") or entry.get("receiver_username")
            content = entry.get("content", "")
            timestamp = entry.get("timestamp") or entry.get("created_at") or ""
            msg_id = entry.get("msg_id") or entry.get("id")

            parsed = self._decode_message_payload(content)

            if msg_type == "system" or sender == "__system__":
                record = self._create_message_record(
                    f"sys:{msg_id}",
                    "__system__",
                    content,
                    timestamp,
                    edited=False,
                    system=True
                )
                self._store_message("General", record)
            elif msg_type == "private":
                partner = sender if sender != self.username else receiver
                if not partner:
                    continue

                record = self._create_message_record(
                    msg_id,
                    sender,
                    content,
                    timestamp,
                    edited=False,
                    chat_partner=partner,
                    private=True,
                    to=receiver,
                    message_type=parsed["kind"],
                    caption=parsed.get("caption", ""),
                    filename=parsed.get("filename"),
                    image_bytes=parsed.get("image_bytes")
                )
                self._store_message(partner, record)
            else:
                record = self._create_message_record(
                    msg_id,
                    sender,
                    content,
                    timestamp,
                    edited=False,
                    message_type=parsed["kind"],
                    caption=parsed.get("caption", ""),
                    filename=parsed.get("filename"),
                    image_bytes=parsed.get("image_bytes")
                )
                self._store_message("General", record)

        self.refresh_direct_messages_list()
        self.refresh_ui_chat()

    def append_message(self, msg_id, username, content, timestamp):
        parsed = self._decode_message_payload(content)
        record = self._create_message_record(msg_id, username, content, timestamp, edited=False, message_type=parsed["kind"], caption=parsed.get("caption", ""), filename=parsed.get("filename"), image_bytes=parsed.get("image_bytes"))
        self._store_message("General", record)
        if self.active_chat_target is None:
            self.draw_bubble(record)
            self.scroll_chat_to_bottom()

    def _build_message_time_label(self, timestamp, is_me=False):
        c = self._theme()
        time_lbl = QLabel(timestamp)
        if is_me:
            time_color = "#E8D8FF" if self.theme == "dark" else "#6A35F0"
        else:
            time_color = "#A8B8D8" if self.theme == "dark" else "#6B7280"
        time_lbl.setStyleSheet(f"""
            color: {time_color};
            font-size: 11px;
            background: transparent;
        """)
        return time_lbl

    def draw_system_message(self, text):
        c = self._theme()
        bubble = QLabel(text)
        bubble.setAlignment(Qt.AlignCenter)
        bubble.setStyleSheet(f"""
            color: {c["muted"]};
            font-style: italic;
            padding: 8px 12px;
            font-size: 12px;
            background: {'rgba(255,255,255,0.75)' if self.theme == "light" else 'rgba(15, 23, 42, 0.38)'};
            border: 1px solid {c["border"]};
            border-radius: 14px;
        """)

        line = QHBoxLayout()
        line.addStretch()
        line.addWidget(bubble)
        line.addStretch()

        self.chat_area_layout.addLayout(line)

    def draw_bubble(self, record):
        msg_id = record["id"]
        username = record["sender"]
        content = record["content"]
        timestamp = record["timestamp"]
        edited = record.get("edited", False)
        message_type = record.get("message_type", "text")

        is_me = (username == self.username)
        display_name = "You" if is_me else username
        c = self._theme()

        row = QWidget()
        row_lay = QHBoxLayout(row)
        row_lay.setContentsMargins(0, 0, 0, 0)
        row_lay.setSpacing(12)

        avatar = AvatarStatusWidget(username, avatar_size=40, is_me=is_me, online=(username in self.current_users) or is_me, show_status=True, border_color=c["window"])
        avatar.set_online((username in self.current_users) or is_me)

        stack = QVBoxLayout()
        stack.setSpacing(4)

        meta_row = QHBoxLayout()
        meta_row.setSpacing(8)

        name_lbl = QLabel(display_name)
        if is_me:
            name_color = "#F8EFFF" if self.theme == "dark" else "#6A35F0"
        else:
            name_color = "#D8E4FF" if self.theme == "dark" else "#1F2937"
        name_lbl.setStyleSheet(f"""
            color: {name_color};
            font-size: 14px;
            font-weight: bold;
            background: transparent;
        """)

        time_lbl = self._build_message_time_label(timestamp, is_me)

        meta_row.addWidget(name_lbl)
        meta_row.addWidget(time_lbl)
        meta_row.addStretch()

        bubble = QFrame()
        bubble.msg_id = msg_id
        bubble.sender = username
        bubble.original_time = timestamp
        bubble.time_label = time_lbl
        bubble.message_type = message_type

        bubble.setContextMenuPolicy(Qt.CustomContextMenu)
        bubble.customContextMenuRequested.connect(
            lambda pos, b=bubble: self.show_message_menu(b, pos)
        )

        bubble.setStyleSheet(self._bubble_stylesheet(is_me))

        bubble_shadow = QGraphicsDropShadowEffect(bubble)
        bubble_shadow.setBlurRadius(26)
        bubble_shadow.setOffset(0, 8)
        bubble_shadow.setColor(QColor(12, 18, 34, 120 if self.theme == "dark" else 38))
        bubble.setGraphicsEffect(bubble_shadow)

        bubble_lay = QVBoxLayout(bubble)
        bubble_lay.setContentsMargins(15, 10, 15, 10)
        bubble_lay.setSpacing(4)

        edited_lbl = QLabel("edited")
        edited_lbl.setVisible(bool(edited))
        edited_color = "rgba(255,255,255,0.85)" if (is_me and self.theme == "dark") else c["accent"]
        edited_lbl.setStyleSheet(f"""
            color: {edited_color};
            font-size: 10px;
            font-weight: bold;
            background: transparent;
            letter-spacing: 1px;
            text-transform: uppercase;
        """)
        bubble.edited_label = edited_lbl

        if message_type == "image":
            raw = record.get("image_bytes")
            pixmap = self._pixmap_from_bytes(raw)
            image_label = ClickableLabel()
            image_label.setAlignment(Qt.AlignCenter)
            image_label.setCursor(Qt.PointingHandCursor)
            image_label.setStyleSheet("background: transparent; border: none;")
            image_label.setMaximumSize(360, 260)
            image_label.setScaledContents(False)

            def _open_preview(p=pixmap, title=record.get("filename") or "Picture"):
                self._open_image_preview(p, title)

            image_label.clicked.connect(_open_preview)

            if not pixmap.isNull():
                thumb = pixmap.scaled(360, 260, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                image_label.setPixmap(thumb)
            else:
                image_label.setText("Image unavailable")
                image_label.setStyleSheet(f"color: {c['muted']}; background: transparent;")

            bubble_lay.addWidget(edited_lbl)
            bubble_lay.addWidget(image_label)

            caption = record.get("caption", "").strip()
            bubble.caption_text = caption
            bubble.msg_label = None
            if caption:
                caption_lbl = QLabel()
                caption_lbl.setWordWrap(True)
                caption_lbl.setTextFormat(Qt.PlainText)
                caption_lbl.setStyleSheet(f"""
                    color: {'#FFFFFF' if is_me else ('#D8E3F5' if self.theme == "dark" else '#1F2937')};
                    font-size: 14px;
                    background: transparent;
                    border: none;
                    padding: 0px;
                    margin: 0px;
                    line-height: 20px;
                """)
                caption_lbl.setText(caption)
                bubble_lay.addWidget(caption_lbl)
        else:
            msg_label = QLabel()
            msg_label.setWordWrap(True)
            msg_label.setTextFormat(Qt.PlainText)
            msg_label.setStyleSheet(f"""
                color: {'#FFFFFF' if is_me else ('#D8E3F5' if self.theme == "dark" else '#1F2937')};
                font-size: 14px;
                background: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
                line-height: 20px;
            """)
            msg_label.setText(self.format_message_text(content))
            bubble.msg_label = msg_label
            bubble_lay.addWidget(edited_lbl)
            bubble_lay.addWidget(msg_label)

        stack.addLayout(meta_row)
        stack.addWidget(bubble)

        if is_me:
            row_lay.addStretch()
            row_lay.addLayout(stack)
            row_lay.addWidget(avatar, alignment=Qt.AlignTop)
        else:
            row_lay.addWidget(avatar, alignment=Qt.AlignTop)
            row_lay.addLayout(stack)
            row_lay.addStretch()

        self.chat_area_layout.addWidget(row)
        self.message_widgets[msg_id] = bubble
        self.scroll_chat_to_bottom()

    def _bubble_stylesheet(self, is_me):
        c = self._theme()
        if is_me:
            return f"""
                QFrame {{
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:1,
                        stop:0 {c["accent"]},
                        stop:1 {c["accent_2"]}
                    );
                    border-radius: 18px;
                    border-top-right-radius: 6px;
                    border: 1px solid rgba(255,255,255,0.12);
                }}
            """
        if self.theme == "dark":
            return """
                QFrame {
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:1,
                        stop:0 #18243A,
                        stop:1 #111B2E
                    );
                    border-radius: 18px;
                    border-top-left-radius: 6px;
                    border: 1px solid rgba(134, 158, 196, 0.18);
                }
            """
        return """
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255,255,255,0.90),
                    stop:0.55 rgba(245,240,255,0.92),
                    stop:1 rgba(236,242,255,0.92)
                );
                border-radius: 18px;
                border-top-left-radius: 6px;
                border: 1px solid rgba(140, 120, 200, 0.18);
            }
        """

    def show_message_menu(self, bubble, pos):
        c = self._theme()
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {c["card_2"]};
                color: {c["text"]};
                border: 1px solid {c["border"]};
            }}
            QMenu::item:selected {{
                background-color: {c["accent"]};
            }}
        """)

        copy_action = menu.addAction("Copy")
        send_action = None
        edit_action = None

        if bubble.sender != self.username:
            send_action = menu.addAction("Send Message")
        elif getattr(bubble, "message_type", "text") == "text":
            edit_action = menu.addAction("Edit")

        chosen = menu.exec_(bubble.mapToGlobal(pos))

        if chosen == copy_action:
            if hasattr(bubble, "msg_label") and bubble.msg_label is not None:
                QApplication.clipboard().setText(bubble.msg_label.text().replace("<br>", "\n"))
            else:
                QApplication.clipboard().setText(getattr(bubble, "caption_text", "Picture"))
        elif send_action is not None and chosen == send_action:
            self.open_private_chat(bubble.sender)
        elif edit_action is not None and chosen == edit_action:
            self.begin_edit(bubble, bubble.msg_label)

    def begin_edit(self, bubble, msg_label):
        if getattr(bubble, "message_type", "text") != "text":
            return
        self.editing_msg_id = bubble.msg_id
        self.editing_bubble = bubble

        doc = QTextDocument()
        doc.setHtml(msg_label.text())
        self.msg_input.setPlainText(doc.toPlainText())
        self.msg_input.setFocus()

    def handle_remote_edit(self, *args):
        if len(args) >= 2:
            msg_id = args[0]
            new_text = args[1]
            self._apply_message_edit(msg_id, new_text)

    def apply_edit(self, msg_id, new_text):
        self._apply_message_edit(msg_id, new_text)

    def _apply_message_edit(self, msg_id, new_text):
        for chat_key, history in self.messages_store.items():
            for i, record in enumerate(history):
                if record["id"] == msg_id:
                    record["content"] = new_text
                    record["edited"] = True
                    history[i] = record

        bubble = self.message_widgets.get(msg_id)
        if bubble is not None and getattr(bubble, "message_type", "text") == "text" and hasattr(bubble, "msg_label"):
            bubble.msg_label.setText(self.format_message_text(new_text))
            if hasattr(bubble, "edited_label"):
                bubble.edited_label.setVisible(True)

        self.refresh_current_chat_if_message_visible(msg_id)

    def refresh_current_chat_if_message_visible(self, msg_id):
        if msg_id in self.message_widgets:
            return

    # ============================================================
    #                    MESSAGE SENDING / ROUTING
    # ============================================================
    def trigger_send(self):
        text = self.msg_input.toPlainText().strip()
        if not text:
            return

        if text.lower() == "/ips":
            self.client.send_command("/ips")
            self.msg_input.clear()
            self.msg_input.setFixedHeight(34)
            self.msg_input.setFocus()
            return

        if self.editing_msg_id is not None:
            self.client.send_edit(self.editing_msg_id, text)
            self.editing_msg_id = None
            self.editing_bubble = None
        else:
            if self.active_chat_target is None:
                self.client.send_message(text)
            else:
                self.client.send_private_message(self.active_chat_target, text)

        self.msg_input.clear()
        self.msg_input.setFixedHeight(34)

    def handle_public_incoming(self, *args):
        if len(args) < 4:
            return

        if len(args) == 4:
            msg_id, username, content, timestamp = args
        else:
            msg_id, username, content, timestamp = args[:4]

        parsed = self._decode_message_payload(content)
        record = self._create_message_record(msg_id, username, content, timestamp, edited=False, message_type=parsed["kind"], caption=parsed.get("caption", ""), filename=parsed.get("filename"), image_bytes=parsed.get("image_bytes"))
        self._store_message("General", record)

        if self.active_chat_target is None:
            self.draw_bubble(record)
            self.scroll_chat_to_bottom()

    def handle_private_incoming(self, *args):
        if len(args) < 4:
            return

        msg_id = None
        sender = None
        content = None
        timestamp = None
        to = None
        edited = False

        if len(args) == 4:
            sender, content, timestamp, to = args
        elif len(args) >= 5 and (
            isinstance(args[0], int) or (isinstance(args[0], str) and str(args[0]).startswith("pm:"))
        ):
            msg_id, sender, content, timestamp, to = args[:5]
        elif len(args) >= 5:
            sender, content, timestamp, to, msg_id = args[:5]
        else:
            sender, content, timestamp, to = args[:4]
            if len(args) >= 5:
                msg_id = args[4]

        partner = sender if sender != self.username else to

        if partner not in self.messages_store:
            self.messages_store[partner] = []

        if msg_id is None:
            msg_id = self._stable_private_message_id(sender, partner, timestamp, content)

        parsed = self._decode_message_payload(content)
        record = self._create_message_record(
            msg_id,
            sender,
            content,
            timestamp,
            edited=edited,
            chat_partner=partner,
            private=True,
            to=to,
            message_type=parsed["kind"],
            caption=parsed.get("caption", ""),
            filename=parsed.get("filename"),
            image_bytes=parsed.get("image_bytes")
        )
        self._store_message(partner, record)

        self.refresh_direct_messages_list()

        if self.active_chat_target == partner:
            self.draw_bubble(record)
            self.scroll_chat_to_bottom()

    # ============================================================
    #                        INPUT BEHAVIOR
    # ============================================================
    def dynamic_input_height(self):
        doc = self.msg_input.document()
        new_h = min(max(34, doc.size().height() + 10), 120)
        self.msg_input.setFixedHeight(new_h)

    def eventFilter(self, obj, event):
        if obj == self.msg_input and event.type() == QEvent.KeyPress:
            key = event.key()
            mods = event.modifiers()

            if key in (Qt.Key_Return, Qt.Key_Enter) and mods & Qt.ShiftModifier:
                self.msg_input.insertPlainText("\n")
                return True

            if key in (Qt.Key_Return, Qt.Key_Enter):
                self.trigger_send()
                return True

        return super().eventFilter(obj, event)

    # ============================================================
    #                 SYSTEM / STATUS MESSAGES
    # ============================================================
    def append_system_message(self, text):
        record = self._create_message_record(
            f"sys:{hashlib.sha1(text.encode('utf-8')).hexdigest()[:12]}",
            "__system__",
            text,
            "",
            edited=False,
            system=True
        )
        self._store_message("General", record)

        if self.active_chat_target is None or text.startswith("Connected users IPs:"):
            self.draw_system_message(text)
            self.scroll_chat_to_bottom()

    # ============================================================
    #                        MISC / HELPERS
    # ============================================================
    def format_message_text(self, text):
        return text

    def closeEvent(self, event):
        try:
            if hasattr(self, "client") and self.client is not None:
                self.client.disconnect()
        except Exception:
            pass
        event.accept()


# ============================================================
#                         APP LAUNCHER
# ============================================================
if __name__ == "__main__":
    app = QApplication([])
    window = ChatWindow()
    window.show()
    app.exec()
