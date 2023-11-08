import socket
import json

class Database():
    HOST = "localhost"
    PORT = 7999

    db_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_socket():
        try:
            Database.db_socket.connect((Database.HOST, Database.PORT))
        except OSError as e:
            pass

    def send_message(message:bytes):
        try:
            Database.db_socket.sendall(message)
        except OSError:
            Database.connect_socket();
            Database.send_message(message)

    def receive_message(size: int = 1024):
        return Database.__rec_message(0, size)
    
    def __rec_message(num, size):
        if num < 2:
            try:
                data = Database.db_socket.recv(size)
            except ConnectionError as e:
                print(type(e), e)
                Database.connect_socket()
                data = Database.__rec_message(num+1,size)
            return data
        else: return b"{}"
    
    def get_tweets():
        msg_dict = {"type": "GET"}
        message = json.dumps(msg_dict).encode()
        Database.send_message(message);
        resp = Database.receive_message()
        resp = json.loads(resp)
        try:
            if resp['type'] == "GET-RESPONSE":
                if resp["payload-type"] == "DB":
                    return resp["db"]
            else:
                return None
        except KeyError:
            return None
    
    def set_tweet(tweet_id, tweet, cookie):
        msg_dict = {"type":"SET",
                    "key": tweet_id,
                    "author": cookie["username"],
                    "value": tweet}
        message = json.dumps(msg_dict).encode()
        Database.send_message(message)
        resp = json.loads(Database.receive_message())
        if resp["type"] == "SET-RESPONSE":
            return resp["success"]
        else:
            return False
        
        

def main():

    # t_id = "other_key"
    # cookie = {"username":"manuel", "session-id":"agafvDASASDCa-fasdf"}
    # tweet = "Holi serv!"

    # Database.set_tweet(t_id, tweet, cookie)

    print(Database.get_tweets())


if __name__ == "__main__":
    main()