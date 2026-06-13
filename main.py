import socket
import threading
import logging

from config import (
    HOST,
    PORT
)

from client_handler import (
    handle_client
)

logging.basicConfig(
    filename="server.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)


def start_server():

    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server.bind(
        (HOST, PORT)
    )

    server.listen()

    print("=" * 40)
    print("SERVER BERJALAN")
    print(f"{HOST}:{PORT}")
    print("=" * 40)

    while True:

        conn, addr = server.accept()

        print(
            f"Connection from {addr}"
        )

        threading.Thread(
            target=handle_client,
            args=(conn, addr),
            daemon=True
        ).start()


if __name__ == "__main__":

    start_server()