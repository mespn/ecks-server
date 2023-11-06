import socket
import threading
import sys
import os
import traceback
from http_parser import *
from http_responses import response_header, full_header, full_response

# =================================
# Custom exceptions
# =================================
class BadRequestError(Exception):
    # Just to differenciate a bad request
    pass

class InternalError(Exception):
    # Just to differenciate an internal server error (500)
    pass


# -------------------------------------------------
# find_file(path)
#
# Tries to open the file in `path`. Returns True if 
# the file exists, False otherwise
# 
# path - a valid absolute path
# 
# returns a boolean value representing whether or not the file exists
# -------------------------------------------------
def find_file(path):
    try:
        f = open(path, 'rb')
        f.close()
    except FileNotFoundError:
        return False

    return True

def check_is_directory(path):
    try:
        f = open(path, 'rb')
        f.close()
    except Exception as e:
        tp = type(e)
        if (tp == IsADirectoryError or 
            tp == PermissionError):
            path = os.path.join(path, "index.html")

    return path

def send_response(socket, message):
    socket.sendall(b"".join((message, b"\r\n")))

def send_head(socket, path, code = 200):
    message = full_header(code, path)
    send_response(socket, message)

def send_body(socket, path, code = 200):
    message = full_response(code, path)
    send_response(socket, message)

def send_error(socket, error_code, server_path):
    error_code = str(error_code)
    error_page = os.path.join(server_path, error_code + ".html")
    if find_file(error_page):
        send_body(socket, error_page, code = error_code)
    else:
        send_response(socket, response_header(error_code))

# -------------------------------------------------
# process_request(socket, method, path) raises BadRequestError, FileNotFoundError, InternalError
#
# send the appropriate response to the received request
# 
# socket - a socket object with open communication
# req - the request as key-value pairs
# 
# returns the list with the transformations done to it 
# -------------------------------------------------
def process_request(socket: socket.socket, req:dict):
    try: 
        method = req["Method"]
        path = req["Path"] # An absolute path

    except KeyError:
        raise InternalError

    path = check_is_directory(path)

    if not find_file(path):
        raise FileNotFoundError

    if method == "GET":
        send_body(socket, path)

    elif method == "HEAD":
        send_head(socket, path)

    else:
        send_response(socket, 400)

# -------------------------------------------------
# handle_client(sock, path)
#
# [Add description]
# 
# sock - 
# path -
# 
# returns 
# -------------------------------------------------

def handle_client(sock: socket.socket, server_path: str):
    data = sock.recv(1024)
    if data:
        try:
            headers = parse_request(data)
            headers["Path"] = server_path + headers["Path"]
        except BadRequestError:
            send_error(sock, 400, server_path)
            return
        
        except TypeError:
            send_error(sock, 500, server_path)
            return
    else:
        return
   
    try:
        process_request(sock, headers)

    except BadRequestError:
        send_error(sock, 400, server_path)
        return
        
    except TypeError:
        send_error(sock, 500, server_path)
        return
    
    except FileNotFoundError:
        send_error(sock, 404, server_path)
    
def main(args):
    PATH = os.path.abspath("ecks")

    # address constants
    HOST = ""
    PORT = 8200

    # set socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # start server
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    while True:
        try:
            (conn, addr) = server_socket.accept()
            conn.settimeout(5)
            aThread = threading.Thread(target = handle_client, args = (conn, PATH))
            aThread.start()
            
        
        # Possible exceptions and dealing with them
        except socket.timeout as e:
            print('timeout')
            continue

        except KeyboardInterrupt:
            print("\nSee you later")
            server_socket.close()
            sys.exit(0)
    
        except BrokenPipeError as e:
            print("Connection was lost", e)
            continue
            
        except MemoryError as e:
            print(e)
            traceback.print_exc()
            sys.exit(1)
        
        except RuntimeError as e:
            print("Thread limit:",threading.active_count())
            print("Exception thread:",threading.current_thread())
            sys.exit(1)

        except Exception as e:
            print("Something happened...: ", e)
            #traceback.print_exc()
            continue

if __name__ == '__main__':
    main(sys.argv)