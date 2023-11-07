import socket

def send_db_message(sock, message):
    sock.sendall(message)

def get_tweets(db_socket):
    # msg = {"type": "GET"}
    # msg = msg.dumps()
    # send_db_message(db_socket, msg)
    print("Tweets :D")

def set_tweet(db_socket, request):
    print("tweet set correctly")

def update_tweet(db_socket, request, tweet_id):
    print("tweet updated correctly")