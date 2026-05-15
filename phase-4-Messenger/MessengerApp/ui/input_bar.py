from PySide6.QtCore import Qt, QEvent


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


def trigger_send(self):
    text = self.msg_input.toPlainText().strip()
    if not text:
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