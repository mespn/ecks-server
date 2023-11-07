import socket
import threading
import sys
import os
import traceback
import uuid
import re
from http_parser import *
from http_responses import response_header, full_header, full_response, api_header
from http_exceptions import *

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

def path_is_api(path):
    try:
        p = path.strip("/").split("/")
        return p[0] == "api"
    except:
        raise BadRequestError

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

def send_error(socket, error_code, server_path = None):
    error_code = str(error_code)

    if server_path:
        error_page = os.path.join(server_path, error_code + ".html")
    else:
        error_page = ""

    if find_file(error_page):
        send_body(socket, error_page, code = error_code)
    else:
        send_response(socket, response_header(error_code))

def login(sock, request):
    headers = ["Set-Cookie: sessionID=" + str(uuid.uuid4()),
               "Set-Cookie: username=" + request["Content"]["username"]
               ]
    msg = api_header(headers)
    send_response(sock, msg)

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
# handle_api(request)
#
# [Add description]
# 
# request - 
# 
# returns 
# -------------------------------------------------
def handle_api(client_socket, request, db_socket = None): 
    clean_path = request["Path"].strip("/")
    if clean_path == "api/login" and request["Method"] == "POST":
        login(client_socket, request)
    else:
        try:
            cookies = parse_cookie(request["Cookie"])

            if "sessionID" not in cookies.keys():
                raise ForbiddenError

            if clean_path == "api/tweet":
                if request["Method"] == "GET":
                    get_tweets(db_socket, request)
                elif request["Method"] == "POST":
                    set_tweet(db_socket, request)
            
            elif re.match("^api\/login\/.*$",clean_path):
                tweet_id = clean_path.split("/")[-1]
                if request["Method"] == "PUT":
                    update_tweet(db_socket, request, tweet_id)
            else:
                send_error(client_socket, 400)

        except KeyError:
            raise ForbiddenError
        

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
            if path_is_api(headers["Path"]):
                handle_api(sock, headers)
            else:
                headers["Path"] = server_path + headers["Path"]
                process_request(sock, headers)
        except BadRequestError:
            send_error(sock, 400, server_path)
            return
        
        except TypeError:
            send_error(sock, 500, server_path)
            return
        
        except FileNotFoundError:
            send_error(sock, 404, server_path)
            return
        
        except ForbiddenError:
            send_error(sock, 401, server_path)
            return
    else:
        return
    
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