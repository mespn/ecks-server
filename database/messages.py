import json

# Coordinator -> worker
def get_database(): 
    '''Works for Coordinator->Worker and 
    web server -> db server'''
    msg_dict = {"type":"GET"}
    return json.dumps(msg_dict).encode()

def set_tweet(id, tweet):
    msg_dict = {"type":"SET", "id":id, "obj": tweet}
    return json.dumps(msg_dict).encode()

def lock():
    msg_dict = {"type":"LOCK"}
    return json.dumps(msg_dict).encode()

# Web Server -> DB Server
def create_tweet(author, tweet):
    msg_dict = {"type":"SET", "author":author, "content":tweet}
    return json.dumps(msg_dict).encode()

def update_tweet(id, author, tweet):
    msg_dict = {"type":"UPDATE", "id":id, "author":author, "content":tweet}
    return json.dumps(msg_dict).encode()

# ====================================================================================
# Responses
def response_get(db):
    msg_dict = {"type":"GET-RESPONSE","payload-type":"DB", "db":db}
    return json.dumps(msg_dict).encode()

def response_lock(bool_value):
    msg_dict = {"type":"LOCK-RESPONSE","success": bool_value}
    return json.dumps(msg_dict).encode()

def response_set(bool_value):
    msg_dict = {"type":"SET-RESPONSE","success": bool_value}
    return json.dumps(msg_dict).encode()

def response_update(bool_value):
    msg_dict = {"type":"UPDATE-RESPONSE", "success":bool_value}
    return json.dumps(msg_dict).encode()

def error(scope, dets):
    msg_dict = {"type":"ERROR", "scope":scope, "dets":dets}
    return json.dumps(msg_dict).encode()

def internal_error(dets):
    return error("SERVER", dets)

def request_error(dets):
    return error("REQUEST", dets)