import socket
import logging

HOST = "127.0.0.1"
PORT = 5000

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((HOST, PORT))
        logging.info("Connected to server")

        # ===== ارسال خودکار پیام اولیه و دریافت پاسخ =====
        greeting = "Hello Server!"
        client.sendall(greeting.encode())
        # این پیام فقط در سرور لاگ می‌شود، در کلاینت لاگ نمی‌کنیم

        data = client.recv(1024).decode()
        if not data:
            logging.warning("Server closed the connection during greeting.")
            return

        logging.info(f"Server: {data}")  # Hi Client!

        # ===== حلقه‌ی اصلی (تقریباً همان کد خودت) =====
        while True:
            message = input("You: ")
            try:
                client.sendall(message.encode())
            except (BrokenPipeError, ConnectionResetError):
                logging.warning("Server disconnected while sending message.")
                break

            if message.lower() == "exit":
                logging.info("Closing connection...")
                # سرور پاسخ "Connection closed by server." یا هر پیام نهایی دیگری می‌فرستد
                try:
                    data = client.recv(1024).decode()
                    if data:
                        logging.info(f"Server: {data}")
                except (BrokenPipeError, ConnectionResetError):
                    pass
                break

            try:
                data = client.recv(1024).decode()
            except (BrokenPipeError, ConnectionResetError):
                logging.warning("Server disconnected unexpectedly.")
                break

            if not data:
                logging.warning("Server closed the connection.")
                break

            logging.info(f"Server: {data}")

    except ConnectionRefusedError:
        logging.error("Could not connect to server. Make sure the server is running.")

    finally:
        client.close()
        logging.info("Client closed")


if __name__ == "__main__":
    start_client()
