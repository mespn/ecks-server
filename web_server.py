import socket
import threading
import sys
import os
import json
import traceback
import uuid
from http_parser import *
from http_responses import response_header, full_header, full_response, api_header
from http_exceptions import *
from db_comms import Database
import http_dictionaries

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
    # print("Message sent is:", message.decode())
    socket.sendall(b"".join((message, b"\r\n")))

def send_head(socket, path, code = 200):
    message = full_header(code, path)
    send_response(socket, message)

def send_body(socket, path, code = 200):
    message = full_response(code, path)
    send_response(socket, message)

def send_inline_body(socket, content, content_type = http_dictionaries.MIME_TYPES[".json"], code = 200):
    message = b"".join((response_header(code), b"Content-Type: " + content_type.encode() + b"\r\nContent-Length: " + str(len(content)).encode()))
    message += b"".join((b"\r\n\r\n", content))
    send_response(socket, message)

def get_tweets(client_socket):
    resp = Database.get_tweets()

    if resp["type"] == "GET-RESPONSE":
        tweets = json.dumps(resp["db"]).encode()
        send_inline_body(client_socket, tweets)
    else:
        raise InternalError
    
def create_tweet(client_socket, tweet_cont, cookies):
    resp = Database.create_tweet(tweet = tweet_cont, cookie= cookies)
    print(resp)
    resp = json.dumps(resp).encode()
    send_inline_body(client_socket, resp)

def update_tweet(client_socket, tweet_id, req_body, cookies):
    resp = Database.update_tweet(tweet_id, req_body, cookies)
    resp = json.dumps(resp).encode()
    send_inline_body(client_socket, resp)

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
def handle_api(client_socket, request): 
    clean_path = request["Path"].strip("/")
    if clean_path == "api/login" and request["Method"] == "POST":
        login(client_socket, request)
    else:
        try:
            cookies = parse_cookie(request["Cookie"])
        except KeyError:
            raise ForbiddenError

        if "sessionID" not in cookies.keys():
            raise ForbiddenError

        if clean_path == "api/tweet":
            if request["Method"] == "GET":
                get_tweets(client_socket)
            elif request["Method"] == "POST":
                print("Got to web_server.create_tweet")
                create_tweet(client_socket, request["Content"], cookies)
        
        elif clean_path.startswith("api/tweet"):
            tweet_id = clean_path.split("/")[-1]
            print("updater is in tweet: %s" % tweet_id)
            if request["Method"] == "PUT":
                update_tweet(client_socket, tweet_id, request["Content"], cookies)
        else:
            print ("request is", request["Method"], clean_path)
            raise BadRequestError


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
            print("This is a type error")
            traceback.print_exc()
            raise InternalError
        
        except InternalError:
            send_error(sock, 500, server_path)
            return
        
        except FileNotFoundError:
            send_error(sock, 404, server_path)
            return
        
        except ForbiddenError:
            print("Needs to log in")
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

        except Exception as e:
            print("Something happened...: ", e)
            #traceback.print_exc()
            continue

if __name__ == '__main__':
    main(sys.argv)