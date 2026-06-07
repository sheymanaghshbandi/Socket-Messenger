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
    if bubble is not None:
        bubble.msg_label.setText(self.format_message_text(new_text))
        if hasattr(bubble, "edited_label"):
            bubble.edited_label.setVisible(True)

    self.refresh_current_chat_if_message_visible(msg_id)


def handle_public_incoming(self, *args):
    if len(args) < 4:
        return

    if len(args) == 4:
        msg_id, username, content, timestamp = args
    else:
        msg_id, username, content, timestamp = args[:4]

    record = self._create_message_record(msg_id, username, content, timestamp, edited=False)
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

    record = self._create_message_record(
        msg_id,
        sender,
        content,
        timestamp,
        edited=edited,
        chat_partner=partner,
        private=True,
        to=to
    )
    self._store_message(partner, record)

    self.refresh_direct_messages_list()

    if self.active_chat_target == partner:
        self.draw_bubble(record)
        self.scroll_chat_to_bottom()