import socket
import threading
import datetime
import os

def timestamp():
    return datetime.datetime.now().strftime("%H:%M")

def log_message(text):
    if not os.path.exists("logs"):
        os.makedirs("logs")
    fname = f"logs/chat_{datetime.date.today()}.txt"
    with open(fname, "a", encoding="utf-8") as f:
        f.write(text + "\n")

HOST = "127.0.0.1"
PORT = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print(f"[SERVER] Running on {HOST}:{PORT}")

clients = {}
lock = threading.Lock()

def broadcast(message):
    with lock:
        for conn in list(clients.keys()):
            try:
                conn.sendall(message.encode())
            except:
                pass

def handle_client(conn, addr):
    ip = addr[0]

    try:
        username = conn.recv(1024).decode().strip()
    except:
        conn.close()
        return

    with lock:
        clients[conn] = {"username": username, "ip": ip}

    join_msg = f"[{timestamp()}] {username} ({ip}) joined the chat."
    print(join_msg)
    log_message(join_msg)
    broadcast(join_msg)

    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break

            msg = data.decode().strip()

            if msg == "/exit":
                break

            if msg == "/users":
                user_list = "\n".join(
                    [f"- {info['username']} ({info['ip']})" for info in clients.values()]
                )
                conn.sendall(f"[System] Online users:\n{user_list}\n> ".encode())
                continue

            if msg == "/help":
                help_text = (
                    "[System] Commands:\n"
                    "/help  - Show commands\n"
                    "/users - List online users\n"
                    "/ping  - Test latency\n"
                    "/exit  - Leave chat\n"
                )
                conn.sendall(help_text.encode())
                continue

            if msg == "/ping":
                conn.sendall("pong\n> ".encode())
                continue

            full_msg = f"[{timestamp()}] {username} ({ip}): {msg}"
            log_message(full_msg)
            broadcast(full_msg)

        except:
            break

    with lock:
        if conn in clients:
            left_msg = f"[{timestamp()}] {clients[conn]['username']} ({ip}) left the chat."
            print(left_msg)
            log_message(left_msg)
            broadcast(left_msg)
            del clients[conn]

    conn.close()

while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
