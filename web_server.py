import socket
import threading
import sys
import os
from http_parser import parse_request

def handle_client(client: socket.socket):
    message = client.recv(1024)
    msg_dict = parse_request(message)

def main():
    SOCK_ADDR = ("", 8200)
    PATH = os.path.abspath("ecks")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind(SOCK_ADDR)
    server_socket.listen()

    while True:
        try:
            (conn, addr) = server_socket.accept()
            conn.settimeout(5)

            thread = threading.Thread(target= handle_client, args=(conn, addr))
            thread.start()

        except KeyboardInterrupt:
            sys.exit(0)
        except:
            print("Something happened.")

if __name__ == '__main__':
    main()