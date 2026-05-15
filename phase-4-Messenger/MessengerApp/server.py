
import socket
import threading
import json
from datetime import datetime

import database

HOST = "127.0.0.1"
PORT = 5050

clients = {}             # conn -> username
client_addresses = {}    # conn -> addr
lock = threading.Lock()

message_counter = 0


def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def broadcast(packet_dict):
    message_json = json.dumps(packet_dict) + "\n"
    data = message_json.encode("utf-8")
    remove_list = []
    with lock:
        for conn in list(clients.keys()):
            try:
                conn.sendall(data)
            except Exception:
                remove_list.append(conn)
        for conn in remove_list:
            clients.pop(conn, None)
            client_addresses.pop(conn, None)


def broadcast_users_list():
    packet = {"type": "users", "users": list(clients.values())}
    broadcast(packet)


def send_to_client(conn, packet_dict):
    try:
        conn.sendall((json.dumps(packet_dict) + "\n").encode("utf-8"))
    except Exception:
        pass


def send_history(conn, username):
    try:
        history = database.get_history_for_user(username, limit=200)
        send_to_client(conn, {"type": "history", "messages": history})
    except Exception as e:
        print("[DB] history error:", e)


def broadcast_system_message(msg):
    global message_counter
    with lock:
        message_counter += 1
        msg_id = message_counter

    try:
        database.insert_message(
            msg_id=msg_id,
            msg_type="system",
            channel="global",
            sender="SYSTEM",
            receiver=None,
            content=msg,
            timestamp=now_text(),
        )
    except Exception as e:
        print("[DB] system save error:", e)

    packet = {"type": "system", "id": msg_id, "message": msg}
    broadcast(packet)


def send_private_message(outgoing, username, target_user):
    data_to_send = (json.dumps(outgoing) + "\n").encode("utf-8")
    with lock:
        for c, name in list(clients.items()):
            if name == target_user or name == username:
                try:
                    c.sendall(data_to_send)
                except Exception:
                    pass


def handle_client(conn, addr):
    global message_counter
    print(f"[NEW CONNECTION] {addr} connected.")
    buffer = ""
    username = "Unknown"
    left_name = "Unknown"

    try:
        data = conn.recv(1024)
        if not data:
            return

        buffer += data.decode("utf-8")
        if "\n" not in buffer:
            # Wait for a full first packet
            while "\n" not in buffer:
                more = conn.recv(1024)
                if not more:
                    return
                buffer += more.decode("utf-8")

        first_packet, buffer = buffer.split("\n", 1)
        first_packet = json.loads(first_packet)
        username = first_packet.get("username", "Unknown")

        with lock:
            clients[conn] = username
            client_addresses[conn] = addr

        try:
            database.upsert_user(username, last_ip=addr[0], last_seen=now_text())
        except Exception as e:
            print("[DB] user save error:", e)

        # Send persisted history first so reconnects restore chat history.
        send_history(conn, username)

        broadcast_system_message(f"{username} joined the chat")
        broadcast_users_list()

        while True:
            data = conn.recv(1024)
            if not data:
                break

            buffer += data.decode("utf-8")
            while "\n" in buffer:
                msg, buffer = buffer.split("\n", 1)
                if not msg.strip():
                    continue

                try:
                    packet = json.loads(msg)
                except Exception:
                    continue

                ptype = packet.get("type")
                content = packet.get("message", "")
                timestamp = now_text()

                if ptype == "message":
                    with lock:
                        message_counter += 1
                        msg_id = message_counter

                    try:
                        database.insert_message(
                            msg_id=msg_id,
                            msg_type="public",
                            channel="global",
                            sender=username,
                            receiver=None,
                            content=content,
                            timestamp=timestamp,
                        )
                    except Exception as e:
                        print("[DB] public save error:", e)

                    outgoing = {
                        "type": "message",
                        "id": msg_id,
                        "username": username,
                        "message": content,
                        "timestamp": timestamp,
                    }
                    broadcast(outgoing)

                elif ptype == "edit":
                    msg_id = packet.get("id", 0)

                    try:
                        database.update_message_content(msg_id, content)
                    except Exception as e:
                        print("[DB] edit save error:", e)

                    outgoing = {
                        "type": "edit",
                        "id": msg_id,
                        "username": username,
                        "message": content,
                        "timestamp": timestamp,
                    }
                    broadcast(outgoing)

                elif ptype == "private_message":
                    target_user = packet.get("to")
                    if not target_user:
                        continue

                    with lock:
                        message_counter += 1
                        msg_id = message_counter

                    try:
                        database.insert_message(
                            msg_id=msg_id,
                            msg_type="private",
                            channel=None,
                            sender=username,
                            receiver=target_user,
                            content=content,
                            timestamp=timestamp,
                        )
                    except Exception as e:
                        print("[DB] private save error:", e)

                    outgoing = {
                        "type": "private_message",
                        "id": msg_id,
                        "from": username,
                        "to": target_user,
                        "message": content,
                        "timestamp": timestamp,
                    }
                    send_private_message(outgoing, username, target_user)

                elif ptype == "command":
                    command = str(packet.get("command", "")).strip().lower()
                    if command == "/ips":
                        with lock:
                            ip_lines = []
                            for c, name in clients.items():
                                addr_info = client_addresses.get(c)
                                ip = addr_info[0] if addr_info else "Unknown"
                                ip_lines.append(f"{name}: {ip}")
                        message = "Connected users IPs:\n" + ("\n".join(ip_lines) if ip_lines else "No connected users.")
                        send_to_client(conn, {"type": "system", "message": message})

    except Exception as e:
        print("[ERROR]", e)
    finally:
        with lock:
            if conn in clients:
                left_name = clients[conn]
                del clients[conn]
            if conn in client_addresses:
                del client_addresses[conn]
        if left_name != "Unknown":
            broadcast_system_message(f"{left_name} left the chat")
            broadcast_users_list()
        try:
            conn.close()
        except Exception:
            pass


def start_server():
    global message_counter
    print(f"[STARTING SERVER] Listening on {HOST}:{PORT}")

    try:
        database.init_db()
        message_counter = database.get_max_msg_id()
        print(f"[DB] ready. Last message id: {message_counter}")
    except Exception as e:
        print("[DB] initialization warning:", e)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    start_server()
