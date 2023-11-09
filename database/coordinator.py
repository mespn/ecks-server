import socket
import sys
import select
import json
import threading
import messages

class Coordinator:
    def __init__(self, workers: list):
        self.PORT = 7999

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.server_socket.bind(("", self.PORT))
        self.server_socket.listen

        self.onDuty = 0 # Which worker to ask for the db
        self.workers = []
        
        for i in workers:
            connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            (host, port) = i.split(':')
            work_addr = (host, int(port))
            connection.connect(work_addr)
            self.workers.append(connection)
        
        self.run_server()

    def __lock_participant(connection, lst, index):
        connection.sendall(messages.lock())
        try:
            lst[index] = json.loads(connection.recv(1024).decode())
        except ConnectionError as e:
            err_msg = messages.error("SERVER", e)
            connection.sendall(err_msg)

    def handle_request(self, sock, request):
        parsed_request = json.loads(request)
        if parsed_request["type"] == "GET":
            sock.sendall(self.get_db(request))
        elif parsed_request["type"] == "SET":
            num_workers = len(self.workers)
            vote_reqs = [None] * num_workers
            vote_resps = [None] * num_workers
            for i in range(num_workers):
                conn = self.workers[i]
                vote_reqs[i] = threading.Thread(target=Coordinator.__lock_participant, args=(conn, vote_resps, i))
                vote_reqs[i].start()

            for thread in vote_reqs:
                thread.join()

            for i in num_workers:
                if self.locked(vote_resps):
                    for j in num_workers:
                        # TODO
                        pass
        else:
            sock.sendall(messages.server_error("Server"))

    def get_db(self, req):
        self.workers[self.onDuty].sendall(req)
        data = self.workers[self.onDuty].recv(1024)
        self.onDuty += 1
        self.onDuty %= len(self.workers)
        return data


    def run_server(self):
        myReadables = [self.server_socket, ] # not transient
        myWriteables = []

        myClients = [] # are transient
        while True:
            try:
                readable, writeable, exceptions = select.select(
                    myReadables + myClients,
                    [],
                    myReadables,
                    5
                )
                print('released from block')
                for eachSocket in readable:
                    if eachSocket is self.server_socket:
                        # new client

                        conn, addr = self.server_socket.accept()
                        print('Connected by', addr)
                        myClients.append(conn)
                        #... read handled by select, and ... later
                    elif eachSocket in myClients:
                        # read, 
                        data = eachSocket.recv(1024)
                        
                        if data:
                            self.handle_request(eachSocket, data.decode())

                        else:
                            # close this client....
                            # they are closing on us!
                            print("Removing client")
                            myClients.remove(eachSocket)
                
                for problem in exceptions:
                    # ... probably a client socket
                    print("has problem")
                    if problem in myClients:
                        myClients.remove(problem)


                    
            except socket.timeout as e:
                #print('timeout')
                pass
            except KeyboardInterrupt as e:
                print("RIP")
                sys.exit(0)
            except Exception as e:
                print("Something happened... I guess...")
                print(e)        

Coordinator(sys.argv[1:]).run_server()