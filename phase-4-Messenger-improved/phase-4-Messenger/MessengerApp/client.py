import socket
import threading
import json
from PySide6.QtCore import QObject, Signal

class ClientNetwork(QObject):
    message_received = Signal(int, str, str, str)
    # Edits can apply to either public integer ids or private string ids.
    message_edited = Signal(object, str)
    system_message = Signal(str)
    users_update = Signal(list)
    history_received = Signal(list)
    connection_lost = Signal()

    # --- NEW: PRIVATE MESSAGE SIGNAL ---
    # args: (msg_id, sender, content, timestamp, recipient)
    private_message_received = Signal(object, str, str, str, str)

    def __init__(self, host="127.0.0.1", port=5050, username="Me"):
        super().__init__()
        self.host = host
        self.port = port
        self.username = username
        self.socket = None
        self.running = False

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.running = True
            packet = {"type": "hello", "username": self.username}
            self.socket.sendall((json.dumps(packet) + "\n").encode("utf-8"))
            threading.Thread(target=self.receive_loop, daemon=True).start()
            return True
        except Exception as e:
            print("[CLIENT] Connection failed:", e)
            return False

    def send_message(self, content: str):
        if not self.running: return
        packet = {"type": "message", "username": self.username, "message": content}
        try:
            self.socket.sendall((json.dumps(packet) + "\n").encode("utf-8"))
        except: self.disconnect()

    def send_edit(self, msg_id: int, new_text: str):
        if not self.running: return
        packet = {"type": "edit", "username": self.username, "id": msg_id, "message": new_text}
        try:
            self.socket.sendall((json.dumps(packet) + "\n").encode("utf-8"))
        except: self.disconnect()

    # --- NEW: SEND PRIVATE MESSAGE ---
    def send_private_message(self, to_user: str, content: str):
        if not self.running: return
        packet = {
            "type": "private_message",
            "to": to_user,
            "message": content
        }
        try:
            self.socket.sendall((json.dumps(packet) + "\n").encode("utf-8"))
        except: self.disconnect()

    def send_command(self, command: str):
        if not self.running: return
        packet = {
            "type": "command",
            "command": command
        }
        try:
            self.socket.sendall((json.dumps(packet) + "\n").encode("utf-8"))
        except: self.disconnect()

    def receive_loop(self):
        buffer = ""
        try:
            while True:
                data = self.socket.recv(1024)
                if not data: break
                buffer += data.decode("utf-8")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if not line.strip(): continue
                    try:
                        packet = json.loads(line)
                    except: continue

                    ptype = packet.get("type")
                    if ptype == "message":
                        self.message_received.emit(packet["id"], packet["username"], packet["message"], packet["timestamp"])
                    elif ptype == "edit":
                        self.message_edited.emit(packet["id"], packet["message"])
                    elif ptype == "system":
                        self.system_message.emit(packet["message"])
                    elif ptype == "users":
                        self.users_update.emit(packet["users"])
                    elif ptype == "history":
                        self.history_received.emit(packet.get("messages", []))
                    # --- NEW: HANDLE INCOMING PRIVATE PACKET ---
                    elif ptype == "private_message":
                        self.private_message_received.emit(
                            packet.get("id", packet.get("msg_id")),
                            packet["from"],
                            packet["message"],
                            packet["timestamp"],
                            packet["to"]
                        )
        except: pass
        finally: self.disconnect()

    def disconnect(self):
        if self.running:
            self.running = False
            try: self.socket.close()
            except: pass
            self.connection_lost.emit()
