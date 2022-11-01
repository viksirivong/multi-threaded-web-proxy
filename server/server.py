import socket
import threading
from client_handler import *

IP = "127.0.1.1" #socket.gethostbyname(socket.gethostname())
PORT = 8000
ADDR = (IP, PORT)

def main():
    print("[STARTING] Server is starting ...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] Server is listening on {IP}:{PORT}")

    while True:
        connection, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(connection, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    main()