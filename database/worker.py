import sys
import socket
import threading
import json
import messages
import random

class Worker:
    def __init__(self, prt):
        self.tweets = {}
        self.locked_tweets = []
        self.lock_start = None
        self.port = prt
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print("Worker started in port", str(self.port))

    def start_server(self):
        self.socket.bind(("", self.port))
        self.socket.listen()

        while True:
            try:
                (conn, addr) = self.socket.accept()
                print("Connected to ", addr)

                theThread = threading.Thread(target=self.handle_connection, args=(conn, ))
                theThread.start()
            

            except socket.timeout as e:
                #print('timeout')
                pass
            except KeyboardInterrupt as e:
                print("RIP")
                sys.exit(0)
            except Exception as e:
                print("Something happened... I guess...")
                print(e)

    def handle_connection(self, conn):
        msg = conn.recv(1024)
        self.handle_message(conn, msg)

    def handle_message(self, conn, msg):
        print("recieved:", msg)
        parsed_msg = json.loads(msg)
        if parsed_msg["type"] == "GET":
            self.send_db(conn)
        elif parsed_msg["type"] == "LOCK":
            self.send_lock_confirmation(conn, parsed_msg["id"])
            print("Lock confirmation sent")
        elif parsed_msg["type"] == "SET":
            self.send_commit_confirmation(conn, parsed_msg["id"], parsed_msg["obj"])
        else:
            Worker.send_req_error(conn)
    
    def send_req_error(conn):
        conn.sendall(messages.request_error())

    def send_lock_confirmation(self, conn, id):
        print("Locking %s"%id)
        success = id not in self.locked_tweets
        if success:
            self.locked_tweets.append(id)
        else:
            print("Failed to lock %s"%id)

        mesage = messages.response_lock(success)
        conn.sendall(mesage)
        
    def send_commit_confirmation(self, conn, id, obj):
        print("committing %s", id )
        try:
            self.tweets[id] = obj
            message = messages.response_set(True)
            self.locked_tweets.remove(id)
        except Exception:
            message = messages.response_set(False)

        conn.sendall(message)

    def send_db(self, conn):
        message = messages.response_get(self.tweets)
        conn.send(message)
        print("sent:", message)

Worker(int(sys.argv[1])).start_server()