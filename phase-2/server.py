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

clients = {}
client_counter = 0
lock = threading.Lock()


def broadcast(message, sender_conn=None):
    with lock:
        for conn in clients:
            if conn != sender_conn:
                try:
                    conn.sendall(message.encode())
                except:
                    pass


def handle_client(conn, addr, client_id):
    logging.info(f"{client_id} connected from {addr[0]}:{addr[1]} at {datetime.now()}")

    try:
        while True:
            message = conn.recv(1024).decode()

            if not message:
                break

            if message.lower() == "exit":
                break

            log_msg = f"{client_id}: {message}"
            logging.info(log_msg)

            broadcast(log_msg, conn)

            conn.sendall(f"Server received: {message}".encode())

    except ConnectionResetError:
        logging.warning(f"{client_id} disconnected unexpectedly")

    finally:
        with lock:
            del clients[conn]

        conn.close()
        # --- فقط این خط تغییر کرده است ---
        logging.info(f"{client_id} from {addr[0]}:{addr[1]} disconnected")
        broadcast(f"{client_id} left the chat")
def handle_client(conn, addr, client_id):
    logging.info(f"{client_id} connected from {addr[0]}:{addr[1]} at {datetime.now()}")

    try:
        while True:
            message = conn.recv(1024).decode()

            if not message:
                break

            if message.lower() == "exit":
                break

            log_msg = f"{client_id}: {message}"
            logging.info(log_msg)

            broadcast(log_msg, conn)

            conn.sendall(f"Server received: {message}".encode())

    except ConnectionResetError:
        logging.warning(f"{client_id} disconnected unexpectedly")

    finally:
        with lock:
            del clients[conn]

        conn.close()
        
        logging.info(f"{client_id} from {addr[0]}:{addr[1]} disconnected")
        broadcast(f"{client_id} left the chat")



def start_server():
    global client_counter

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    logging.info(f"Server listening on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()

        with lock:
            client_counter += 1
            client_id = f"Client-{client_counter}"
            clients[conn] = client_id

        conn.sendall(f"Welcome {client_id}".encode())
        broadcast(f"{client_id} joined the chat")

        thread = threading.Thread(target=handle_client, args=(conn, addr, client_id))
        thread.start()

        logging.info(f"Active clients: {len(clients)}")


if __name__ == "__main__":
    start_server()
