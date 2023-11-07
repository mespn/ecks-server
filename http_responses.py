import os
import datetime
import pytz
from http_dictionaries import STATUS_CODES, MIME_TYPES

# =================================================
# get_mime_type(path)
#
# 
# path - a valid absolute path to an existing file
#
# return: the appropriate mime type for the file, or its 
#         extension if no corresponding mime type is 
#         available in mime_types.json
#
# =================================================
def get_mime_type(path:str):
    filename = path.split('/?\\?')[-1] # regex to find either / or \
    dot_index = path.index('.')
    extension = filename[dot_index:] 
    try: 
        mime_type = MIME_TYPES[extension]
    except KeyError:
        mime_type = extension
    
    return mime_type

# =================================================
# time_as_string(timestamp)
#
# Formats any given time stamp into the HTTP Date format
#
# timestamp - a float that represents some time
#
# Returns the timestamp as a date in the format accepted 
# by HTTP
#
# =================================================
def time_as_string(timestamp):
    datePattern = "%a, %d %b %Y %H:%M:%S %Z"

    # hardcoding Winnipeg for simplicity
    time = datetime.datetime.fromtimestamp(timestamp, tz=pytz.timezone("America/Winnipeg"))
    forHeader = time.strftime(datePattern)
    return forHeader

# =================================================
# get_modified_date(path)
#
# path - a valid *absolute* path that leads to an existing file
#
# Returns the file in `path`'s Last Modified date and 
# time in the correct date format
#
# =================================================
def get_modified_date(path:str):
    modifiedTimestamp = os.path.getmtime(path)
    return time_as_string(modifiedTimestamp)

# =================================================
# get_current_date()
#
# Returns the current date and time in the correct date format
#
# =================================================
def get_current_date():
    currentTimestamp = datetime.datetime.today().timestamp()
    return time_as_string(currentTimestamp)

# =================================================
# content_header(path)
#
# Note: assumes path leads to an existing file
#
# Gets the file in `path`, its type,  size and Last Modified 
# date and formats it as a string
#
# path - a valid *absolute* path that leads to an existing path
# 
# returns a string in the following format with no leading 
# whitespace and a trailing line break:
# """
# Content-Type: [mime_type] 
# Content-Length: [size]
# Last-Modified: [date]
# """
#
# =================================================
def content_header(path:str):
    content_type = get_mime_type(path)
    content_length = os.stat(path).st_size
    last_modified = get_modified_date(path)

    return "Content-type: {}\r\nContent-Length: {}\r\nLast-Modified: {}\r\n".format(content_type, content_length, last_modified)

# =================================================
# response_body(path)
#
# Note: assumes path leads to an existing file
#
# Reads the file in `path` in binary and returns it
#
# path - a valid *absolute* path that leads to an existing file
# 
# returns the file content as a byte string with a leading
# 
# =================================================
def response_body(path:str):
    with open(path, "rb") as f:
        return f.read()

# =================================================
# response_headers(code)
#
# Formats an HTTP response with the status code `code`
#
# code - a valid HTTP Status Code listed in status_codes.json
# 
# returns a string in HTTP response format with no leading 
# whitespace and a trailing line break
#
# =================================================
def response_header(code:str):
    if type(code) != str:
        code = str(code)
    version = "HTTP/1.1"
    message = STATUS_CODES[code]
    server_name = "Doug Dimmadome"
    return "{} {} {}\r\nServer: {}\r\nDate: {}\r\n".format(version, code, 
                                                       message,server_name, get_current_date()).encode()

def full_header(code, path):
    return (response_header(code).decode() + content_header(path)).encode()

def full_response(code, path):
    header = full_header(code, path)
    body = response_body(path)
    return b"\r\n".join((header,body))

def api_header(headers: list, code: str = "200"):
    base = response_header(code).decode("utf-8")
    for i in headers.keys():
        base += i +"\r\n"
    return (base + "\r\n").encode()