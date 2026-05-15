import socket
import threading
import logging
from datetime import datetime

HOST = "127.0.0.1"
PORT = 5000

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

clients = {}  # conn -> {id, addr}
client_counter = 0
lock = threading.Lock()
server_start_time = datetime.now()
server_running = True


def get_timestamp():
    return datetime.now().strftime("%H:%M")


def send_to_client(conn, message):
    try:
        conn.sendall(message.encode())
    except:
        pass


def list_clients():
    with lock:
        return [clients[c]["id"] for c in clients]


def get_client_by_id(client_id):
    with lock:
        for conn, info in clients.items():
            if info["id"] == client_id:
                return conn
    return None


def handle_client(conn, addr, client_id):
    logging.info(f"{client_id} connected from {addr[0]}:{addr[1]}")

    send_to_client(conn, f"Welcome {client_id}")
    send_to_client(conn, "Type /help for available commands")

    try:
        while True:
            message = conn.recv(1024).decode()
            if not message:
                break

            # -------- COMMAND SYSTEM --------
            if message.startswith("/"):
                parts = message.split()

                if message == "/help":
                    help_text = """
Available commands:
/help - Show commands
/clients - List connected clients
/msg <Client-ID> <message> - Private message
/stats - Server statistics
/quit - Disconnect
"""
                    send_to_client(conn, help_text)

                elif message == "/clients":
                    send_to_client(conn, "Connected clients: " + ", ".join(list_clients()))

                elif parts[0] == "/msg" and len(parts) >= 3:
                    target_id = parts[1]
                    private_msg = " ".join(parts[2:])
                    target_conn = get_client_by_id(target_id)

                    if target_conn:
                        timestamp = get_timestamp()
                        send_to_client(
                            target_conn,
                            f"[{timestamp}] (Private) {client_id}: {private_msg}"
                        )
                        send_to_client(conn, "Private message sent.")
                    else:
                        send_to_client(conn, "Client not found.")

                elif message == "/stats":
                    uptime = datetime.now() - server_start_time
                    send_to_client(
                        conn,
                        f"Active clients: {len(clients)}\nServer uptime: {uptime}"
                    )

                elif message in ["/quit", "exit"]:
                    break

                else:
                    send_to_client(conn, "Unknown command. Type /help.")

            # -------- NORMAL MESSAGE --------
            else:
                timestamp = get_timestamp()
                response = f"[{timestamp}] Server received: {message}"
                send_to_client(conn, response)
                logging.info(f"{client_id}: {message}")

    except ConnectionResetError:
        logging.warning(f"{client_id} disconnected unexpectedly")

    finally:
        with lock:
            if conn in clients:
                del clients[conn]

        conn.close()
        logging.info(f"{client_id} disconnected")


def server_admin_commands(server_socket):
    global server_running
    while server_running:
        cmd = input()

        if cmd == "/shutdown":
            print("Shutting down server...")
            server_running = False
            with lock:
                for conn in list(clients.keys()):
                    send_to_client(conn, "Server is shutting down.")
                    conn.close()
            server_socket.close()
            break

        elif cmd.startswith("/kick"):
            parts = cmd.split()
            if len(parts) == 2:
                target_id = parts[1]
                target_conn = get_client_by_id(target_id)
                if target_conn:
                    send_to_client(target_conn, "You have been kicked by server.")
                    target_conn.close()
                    print(f"{target_id} kicked.")
                else:
                    print("Client not found.")


def start_server():
    global client_counter

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    logging.info(f"Server listening on {HOST}:{PORT}")

    admin_thread = threading.Thread(target=server_admin_commands, args=(server,))
    admin_thread.daemon = True
    admin_thread.start()

    while server_running:
        try:
            conn, addr = server.accept()
        except:
            break

        with lock:
            client_counter += 1
            client_id = f"Client-{client_counter}"
            clients[conn] = {"id": client_id, "addr": addr}

        thread = threading.Thread(target=handle_client, args=(conn, addr, client_id))
        thread.start()

        logging.info(f"Active clients: {len(clients)}")


if __name__ == "__main__":
    start_server()
