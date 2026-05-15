import hashlib


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

    if self.active_chat_target is None:
        self.draw_system_message(text)
        self.scroll_chat_to_bottom()