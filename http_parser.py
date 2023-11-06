from http_exceptions import BadRequestError

def parse_content(content_string: str):
    cont_dict = {}
    pairs = content_string.split("&")
    for i in pairs:
        (key,value) = i.split("=")
        cont_dict[key] = value
    return cont_dict

def check_format(request):
    # First line is not empty
    if request[0] == "":
        raise BadRequestError
    
    # No whitespace before or after each line
    for i in request:
        if i.strip() != i:
           raise BadRequestError
        
    # Each following line is correctly formatted
    for i in request[1:]:
        if i == "":
            request.remove(i)
            continue
        i = i.split(": ",1)
        if len(i) != 2:
            raise BadRequestError

def parse_request(http_request:str):
    '''
    Raises BadRequestError

    http_request - a string

    Verifies that the string is a valid HTTP request, parses it and returns
    a dictionary containing its Method, Path, HTTP version, and headers
    '''
    try:
        http_request = http_request.decode("utf-8")
    except:
        pass

    result = http_request.split("\r\n\r\n")

    headers =result[0]
    content = None
    if len(result) > 1:
        content = result[1]
    
    lines = headers.split("\r\n")
    for i in lines:
        if i == "":
            lines.remove(i)
        else:
            i =i.rstrip()

    # Verifies that the given http_request is a correctly formatted request
    check_format(lines)

    # Create a dictionary 
    parsed_request = dict()
    
    # Split first line into METHOD, PATH, and VERSION
    first_line = lines[0].split()
    parsed_request["Method"] = first_line[0]
    parsed_request["Path"] = first_line[1]
    parsed_request["Version"] = first_line[2]

    # Map each header to its values
    try:
        for i in lines[1:]:
            (key, value) = i.split(": ")
            parsed_request[key] = value
    except:
        raise BadRequestError

    if content:
        parsed_request["Content"] = parse_content(content);

    return parsed_request
