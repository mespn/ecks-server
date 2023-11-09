import socket
import json
from http_exceptions import *
import database.messages as messages

class Database():
    HOST = "localhost"
    PORT = 7999

    def exchange_message(msg):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as db_socket:
                db_socket.connect((Database.HOST, Database.PORT))
                db_socket.sendall(msg)
                return db_socket.recv(1024)
        except:
            raise InternalError
    
    def get_tweets():
        message = messages.get_tweets()
        resp = Database.exchange_message(message)
        resp = json.loads(resp)
        return resp
    
    def create_tweet(tweet, cookie):    
        auth = cookie["username"]
        cont = tweet["Content"]
        message = messages.create_tweet(auth, cont)
        Database.exchange_message(message)
        resp = json.loads(Database.receive_message())
        if resp["type"] == "SET-RESPONSE":
            return resp
        elif resp["type"] == "ERROR":
            raise InternalError
        
    def update_tweet(id, tweet, cookie):
        auth = cookie["username"]
        cont = tweet["Content"]
        message = messages.update_tweet(id, auth, cont)
        resp = Database.exchange_message(message)
        if resp["type"] == "SET-RESPONSE":
            return resp
        else:
            raise InternalError
        

def main():

    # t_id = "other_key"
    # cookie = {"username":"manuel", "session-id":"agafvDASASDCa-fasdf"}
    # tweet = "Holi serv!"

    # Database.set_tweet(t_id, tweet, cookie)

    print(Database.get_tweets())


if __name__ == "__main__":
    main()