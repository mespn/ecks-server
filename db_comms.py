import socket
import json
from http_exceptions import *
import database.messages as messages

class Database():
    HOST = "localhost"#"kingfisher.cs.umanitoba.ca"
    PORT = 8991

    def exchange_message(msg):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as db_socket:
                db_socket.connect((Database.HOST, Database.PORT))
                db_socket.sendall(msg)
                return db_socket.recv(1024)
        except:
            raise InternalError
    
    def get_tweets():
        message = messages.get_database()
        resp = Database.exchange_message(message)
        resp = json.loads(resp)
        return resp
    
    def create_tweet(tweet, cookie):    
        auth = cookie["username"]
        cont = tweet["Content"]
        twt = messages.tweet_obj(auth, cont)
        message = messages.set_tweet("", twt)
        resp =Database.exchange_message(message)
        resp = json.loads(resp)
        if resp["type"] == "SET-RESPONSE":
            return resp
        elif resp["type"] == "ERROR":
            raise InternalError
        
    def update_tweet(id, tweet, cookie):
        auth = cookie["username"]
        cont = tweet["Content"]
        twt = messages.tweet_obj(auth, cont)
        message = messages.set_tweet(id, twt)
        resp = Database.exchange_message(message)
        resp = json.loads(resp)
        if resp["type"] == "SET-RESPONSE":
            return resp
        else:
            raise InternalError
        

def main():

    # t_id = "other_key"
    cookie = {"username":"manuel", "session-id":"agafvDASASDCa-fasdf"}
    # tweet = "Holi serv!"

    # Database.set_tweet(t_id, tweet, cookie)
    tt = {"Content":""}

    tt["Content"] = "Quiero probar esto"
    print(Database.create_tweet(tt, cookie))

    tt["Content"] = "Segundo Tweet"
    print(Database.create_tweet(tt, cookie))

    tweets = Database.get_tweets()

    print(tweets)
    print()
    print("The tweets are: ")
    for i in tweets["db"].keys():
        print(i, tweets["db"][i])


if __name__ == "__main__":
    main()