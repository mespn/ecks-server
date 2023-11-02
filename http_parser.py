from http_exceptions import BadRequestError

def parse_request(http_request:str): # Raises BadRequestError
    '''

    '''
    headers = {}
    lines = http_request.split("\n")
    try:
        for i in lines[1:]:
            (key, value) = i.split(": ")
            headers[key] = value
    except:
        raise BadRequestError

    first = lines[0].split(" ")