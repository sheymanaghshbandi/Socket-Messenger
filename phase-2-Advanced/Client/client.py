import socket
import threading

HOST = "127.0.0.1"
PORT = 5000


def receive_messages(client):
    while True:
        try:
            message = client.recv(1024).decode()
            if not message:
                print("\nDisconnected from server.")
                break
            print(f"\n{message}\n> ", end="")
        except:
            break


def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    print("Connected to server. Type /help for commands.")

    thread = threading.Thread(target=receive_messages, args=(client,))
    thread.daemon = True
    thread.start()

    while True:
        message = input("> ")
        client.sendall(message.encode())

        if message.lower() in ["/quit", "exit"]:
            break

    client.close()


if __name__ == "__main__":
    start_client()
