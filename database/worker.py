import sys
import socket
import time
import json

class Worker:
    def __init__(self, sys_args):
        self.tweets = {}
        self.lock = False
        self.lock_start = None
        self.port = int(sys_args[1])
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def start_server(self):
        self.socket.bind(("", self.port))
        self.socket.listen()

        while True:
            try:
                (conn, addr) = self.socket.accept()
                print("Connected to ", addr)

                msg = conn.recv(1024)
                self.handle_message(conn, msg)
            

            except socket.timeout as e:
                #print('timeout')
                pass
            except KeyboardInterrupt as e:
                print("RIP")
                sys.exit(0)
            except Exception as e:
                print("Something happened... I guess...")
                print(e)

    def handle_message(self, conn, msg):
        parsed_msg = json.loads(msg)
        if parsed_msg["type"] == "GET":
            self.send_db(conn)
        elif parsed_msg["type"] == "SET":
            self._2pc(conn, msg)
        else:
            self.send_error("Unsupported action")
    
    def send_db(self, conn):
        resp = {
            "type": "GET-RESPONSE",
            "payload-type": "DB",
            "db": self.tweets
        }
        message = json.dumps(resp).encode()
        conn.sendall(message)



Worker(sys.argv[1]).start_server()