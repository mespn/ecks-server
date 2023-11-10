import json

# Coordinator -> worker
def get_database(): 
    '''Works for Coordinator->Worker and 
    web server -> db server'''
    msg_dict = {"type":"GET"}
    return json.dumps(msg_dict).encode()

def set_tweet(tweet_id, obj):
    print(tweet_id, obj)
    msg_dict = {"type":"SET", "id":tweet_id, "obj": obj}
    return json.dumps(msg_dict).encode()

def lock(tweet_id):
    msg_dict = {"type":"LOCK", "id":tweet_id}
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

def request_error(dets = "Bad request"):
    return error("REQUEST", dets)

def tweet_obj(author, content):
    return {"author":author, "content":content}