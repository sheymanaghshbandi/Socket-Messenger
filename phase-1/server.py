import socket
import logging
from datetime import datetime

HOST = "127.0.0.1"
PORT = 5000

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    logging.info(f"Server is listening on {HOST}:{PORT}")

    conn = None
    try:
        conn, addr = server.accept()
        logging.info(f"Client connected from {addr[0]}:{addr[1]}")
        logging.info(f"Connection time: {datetime.now()}")

        # ===== مرحله‌ی دست‌دادن (Hello Server! / Hi Client!) =====
        try:
            greeting = conn.recv(1024).decode()
        except ConnectionResetError:
            logging.warning("Client disconnected during greeting")
            return

        if not greeting:
            logging.warning("Client closed connection before sending greeting")
            return

        logging.info(f"Client: {greeting}")  # فقط روی سرور لاگ می‌شود

        # پاسخ اولیه‌ی سرور
        initial_response = "Hi Client!"
        conn.sendall(initial_response.encode())
        # این پاسخ فقط روی کلاینت لاگ می‌شود، نه روی سرور

        # ===== حلقه‌ی اصلی (دقیقاً مثل کد خودت) =====
        while True:
            try:
                message = conn.recv(1024).decode()

                if not message:
                    # کلاینت سوکت را بسته است
                    logging.info("Client closed the connection.")
                    break

                if message.lower() == "exit":
                    logging.info("Client requested to close the connection")
                    conn.sendall("Connection closed by server.".encode())
                    break

                logging.info(f"Client: {message}")

                response = input("Server reply: ")
                conn.sendall(response.encode())

            except ConnectionResetError:
                logging.warning("Client disconnected unexpectedly")
                break

    except KeyboardInterrupt:
        # وقتی سرور را با Ctrl+C می‌بندی
        logging.info("Server interrupted by user (Ctrl+C)")
        if conn:
            try:
                # اطلاع به کلاینت که سرور در حال بسته‌شدن است
                conn.sendall("Server is shutting down.".encode())
            except Exception:
                pass

    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass
        server.close()
        logging.info("Server shut down")


if __name__ == "__main__":
    start_server()
