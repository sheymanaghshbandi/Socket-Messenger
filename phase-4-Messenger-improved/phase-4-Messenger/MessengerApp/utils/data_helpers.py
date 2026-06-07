import hashlib


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
    self.messages_store[chat_key].append(record)


def _get_preview_text(self, username):
    history = self.messages_store.get(username, [])
    if not history:
        return "Online" if username in self.current_users else "No messages yet"

    last = history[-1]
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


def _stable_private_message_id(self, sender, receiver, timestamp, content):
    payload = f"{sender}|{receiver}|{timestamp}|{content}"
    digest = hashlib.sha1(payload.encode("utf-8")).hexdigest()
    return f"pm:{digest[:20]}"


def _extract_message_args(self, args, expected_names):
    values = list(args)
    if len(values) == len(expected_names):
        return values
    return values[:len(expected_names)]