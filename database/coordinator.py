import socket
import sys
import select
import json
import threading
import uuid
import messages
import traceback

class Coordinator:
    def __init__(self, workers: list):
        self.PORT = 8991

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.onDuty = 0 # Which worker to ask for the db
        self.worker_addresses = []
        
        for i in workers:
            addr = i.split(':')
            addr[1] = int(addr[1])
            print("Registering worker at", addr)
            self.worker_addresses.append(tuple(addr))
        
        self.run_server()

    def __lock_participant(self, tweet_id, lst, index):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as worker_socket:
                worker_socket.connect(self.worker_addresses[index])
                worker_socket.sendall(messages.lock(tweet_id))
                data = worker_socket.recv(1024)
                lst[index] = json.loads(data)
        except ConnectionError as e:
            err_msg = messages.internal_error("Could not reach worker")
            lst[index] = err_msg
        return

    def __send_set(self, tweet_id, obj, lst, index):
        print("Sending tweet", tweet_id)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as worker_socket:
                worker_socket.connect(self.worker_addresses[index])
                worker_socket.sendall(messages.set_tweet(tweet_id, obj))
                lst[index] = json.loads(worker_socket.recv(1024))
        except ConnectionError as e:
            lst[index] = messages.internal_error("Could not reach worker")
            return
        except Exception as e:
            lst[index] = messages.internal_error(e)
        return

    def set_tweet(self, tweet_id, obj):
        try:
            num_workers = len(self.worker_addresses)

            worker_threads = [None] * num_workers
            resps = [None]*num_workers

            # Locking
            for i in range(num_workers):
                worker_threads[i] = threading.Thread(target=self.__lock_participant, args=(tweet_id, resps, i))
                worker_threads[i].start()
            
            for thread in worker_threads:
                thread.join()

            correct = 0
            for i in resps:
                if i["type"] == "LOCK-RESPONSE" and i["success"]:
                    correct += 1


            # committing
            if correct == num_workers:
                resps = [None]*num_workers
                for i in range(num_workers):
                    print(i)
                    worker_threads[i] = threading.Thread(target=self.__send_set, args=(tweet_id, obj, resps, i))
                    print("created thread")
                    worker_threads[i].start()
        
                for thread in worker_threads:
                    thread.join(1)

                if None in resps:
                    raise ConnectionError
            
            resp_msg = messages.response_set(True)
        
        except Exception as e:
            resp_msg = messages.response_set(False)
        
        return resp_msg

    def handle_request(self, sock, request):
        try:
            parsed_request = json.loads(request)
        except Exception as e:
            print(e)
            sock.send(messages.request_error("Request is %s \nand has the exception %s"%(request, e.__str__())))
            return
        try:
            if parsed_request["type"] == "GET":
                sock.sendall(self.get_db())
            elif parsed_request["type"] == "SET":
                if parsed_request["id"]=="":
                    tweet_id = str(uuid.uuid4())
                else:
                    tweet_id = parsed_request["id"]

                obj = parsed_request["obj"] 
                sock.sendall(self.set_tweet(tweet_id, obj))

            else:
                sock.sendall(messages.request_error())
        except Exception as e:
            # traceback.print_exc()
            print(e)
            sock.sendall(messages.internal_error(e.__str__()))

    def get_db(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as worker_socket:
            address = self.worker_addresses[self.onDuty]
            worker_socket.connect(tuple(address))
            worker_socket.sendall(messages.get_database())
            data = worker_socket.recv(1024)

        self.onDuty += 1
        self.onDuty %= len(self.worker_addresses)
        return data


    def run_server(self):
        self.server_socket.bind(("", self.PORT))
        self.server_socket.listen()
        
        myReadables = [self.server_socket, ] # not transient
        myWriteables = []

        myClients = [] # are transient
        while True:
            try:
                readable, writeable, exceptions = select.select(
                    myReadables + myClients,
                    [],
                    myReadables
                )
                for eachSocket in readable:
                    if eachSocket is self.server_socket:
                        # new client
                        (conn, addr) = self.server_socket.accept()
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
                # traceback.print_exc()
                

coord = Coordinator(sys.argv[1:])
coord.run_server()