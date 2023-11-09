import socket
import json
import uuid
import messages

class Database():

    with open("test_db.json", "rb") as db_file:
        tweets = json.load(db_file)

    def connect_socket():
        print("Socket not needed")
        # try:
        #     Database.db_socket.connect((Database.HOST, Database.PORT))
        # except OSError as e:
        #     pass

    def send_message(message:bytes):
        print("Message not needed")
        # try:
        #     Database.db_socket.sendall(message)
        # except OSError:
        #     Database.connect_socket();
        #     Database.send_message(message)

    def receive_message(size: int = 1024):
        print("Message not needed")
        # return Database.__rec_message(0, size)
    
    def __rec_message(num, size):
        print("Message not needed")
        # if num < 2:
        #     try:
        #         data = Database.db_socket.recv(size)
        #     except ConnectionError as e:
        #         print(type(e), e)
        #         Database.connect_socket()
        #         data = Database.__rec_message(num+1,size)
        #     return data
        # else: return b"{}"
    
    def get_tweets():
        # msg_dict = {"type": "GET"}
        # message = json.dumps(msg_dict).encode()
        # Database.send_message(message);
        # resp = Database.receive_message()
        # resp = json.loads(resp)
        # try:
        #     if resp['type'] == "GET-RESPONSE":
        #         if resp["payload-type"] == "DB":
        #             return resp["db"]
        #     else:
        #         return None
        # except KeyError:
        #     return None
        msg = messages.response_get(Database.tweets)
        return msg
    
    def set_tweet(tweet, cookie):
        tweet_id = str(uuid.uuid4())
        print(cookie)
        Database.tweets[tweet_id] = {"author": cookie["username"], "content":tweet["Content"]}
        print("most recent tweet is", tweet_id, ":", Database.tweets[tweet_id])
        return messages.response_set(True)
        # msg_dict = {"type":"SET",
        #             "key": tweet_id,
        #             "author": cookie["username"],
        #             "value": tweet}
        # message = json.dumps(msg_dict).encode()
        # Database.send_message(message)
        # resp = json.loads(Database.receive_message())
        # if resp["type"] == "SET-RESPONSE":
        #     return resp["success"]
        # else:
        #     return False
        
    def update_tweet(id, req_content, cookies):
        try:
            Database.tweets[id] = {"author": cookies["username"], "content":req_content["Content"]}
            print(Database.tweets[id])
            return messages.response_set(True)
        except:
            return messages.response_set(False)

        
        

