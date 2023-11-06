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

test = """GET /~robg/get_ip.html HTTP/1.1\r
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7\r
Accept-Encoding: gzip, deflate, br\r
Accept-Language: es-ES,es;q=0.9,en;q=0.8\r
Cache-Control: max-age=0\r
Connection: keep-alive\r
Cookie: _gcl_au=1.1.1932237762.1696958083; _fbp=fb.1.1696958083797.569382494; _tt_enable_cookie=1; _ttp=yRX3IWaVraFPWBB1qEZBAhhuoZc; __gsas=ID=615e199763081232:T=1697509182:RT=1697509182:S=ALNI_MasM42Nv21b7SFw92QO77U3vmldVg; _ga_EV58QL491B=GS1.1.1697687679.4.1.1697687806.0.0.0; _ga=GA1.1.888717666.1696958084; _ga_5KL2MD48DQ=GS1.1.1699051911.13.0.1699051911.60.0.0; Rob=5179\r
Host: home.cs.umanitoba.ca\r
If-Modified-Since: Thu, 05 Oct 2023 15:53:24 GMT\r
If-None-Match: "722-606fa1fb8d67d"\r
Referer: https://universityofmanitoba.desire2learn.com/\r
Sec-Fetch-Dest: document\r
Sec-Fetch-Mode: navigate\r
Sec-Fetch-Site: cross-site\r
Sec-Fetch-User: ?1\r
Upgrade-Insecure-Requests: 1\r
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36\r
sec-ch-ua: "Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"\r
sec-ch-ua-mobile: ?0\r
sec-ch-ua-platform: \"Windows\"\r
\r
k1=v1&k2=v2"""
try:
    d = parse_request(test)
    for i in d.keys():
        print("{}: {}".format(i, d[i]))
except BadRequestError:
    print("Bad request")