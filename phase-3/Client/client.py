import socket
import threading
import sys
import time

RESET  = "\033[0m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
WHITE  = "\033[97m"

HOST = "127.0.0.1"
PORT = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

username = input("Choose a username: ").strip()
client.sendall(username.encode())

print(GREEN + "Connected! Type your message." + RESET)
print("Use /exit to leave.\n")

def receive():
    while True:
        try:
            msg = client.recv(1024).decode()
            if not msg:
                break

            if msg.startswith("[System]") or "joined the chat" in msg or "left the chat" in msg:
                print(YELLOW + msg + RESET)

            elif msg.startswith("[") and f"] {username} (" in msg:
                print(GREEN + msg + RESET)

            else:
                print(WHITE + msg + RESET)

            print("> ", end="")

        except:
            break

def send():
    while True:
        msg = input("> ").strip()

        if msg == "/exit":
            client.sendall(msg.encode())
            time.sleep(0.1)
            client.close()
            sys.exit()

        client.sendall(msg.encode())

threading.Thread(target=receive, daemon=True).start()
send()
