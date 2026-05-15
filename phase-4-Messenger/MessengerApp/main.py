from PySide6.QtWidgets import QApplication
from ui.chat_window import ChatWindow


def main():
    app = QApplication([])
    window = ChatWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
