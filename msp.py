"""
A Python implementation to interact with the MSP API
"""

import hashlib
import binascii
from curl_cffi import requests, CurlHttpVersion
import random
import base64
from datetime import date, datetime
from pyamf import remoting, ASObject, TypedObject, AMF3, amf3
from secrets import token_hex

def _marking_id():
    _int = random.randint(1, 100)
    while True:
        _int += random.randint(1, 2)
        yield _int

# Instantiate the generator
marking_id = _marking_id()
def ticket_header(ticket: str) -> ASObject:
    """
    Generate a ticket header for the given ticket
    """

    loc1bytes = str(next(marking_id)).encode('utf-8')
    loc5 = hashlib.md5(loc1bytes).hexdigest()
    loc6 = binascii.hexlify(loc1bytes).decode()
    return ASObject({"Ticket": ticket + loc5 + loc6, "anyAttribute": None})


def calculate_checksum(arguments):
    no_ticket_value = "XSV7%!5!AX2L8@vn"
    salt = "2zKzokBI4^26#oiP"

    def from_array(arguments):
        o = ""
        for i in arguments:
            o += from_object_inner(i)
        return o

    def from_object_inner(Obj):
        if Obj == None:
            return ""
        if type(Obj) == int or type(Obj) == str:
            return str(Obj)
        if type(Obj) == bool:
            return str(Obj)
        if type(Obj) == bytes:
            return from_byte_array(Obj)
        if type(Obj) == list:
            return from_array(Obj)
        if type(Obj) == dict:
            return from_object(Obj)
        if type(Obj) == date:
            return str(Obj.year) + str(Obj.month - 1) + str(Obj.day)
        if type(Obj) == amf3.ByteArray:
            return from_byte_array(Obj)
        if type(Obj) == ASObject:
            return from_object(Obj)

        return ""

    def from_byte_array(bytes):
        if len(bytes) <= 20:
            return bytes.getvalue().hex()

        num = len(bytes) // 20
        array = bytearray(20)
        for i in range(20):
            bytes.seek(num * i)
            array[i] = bytes.read(1)[0]

        return array.hex()

    def get_ticket_value(arr):
        for obj in arr:
            if isinstance(obj, ASObject) and "Ticket" in obj:
                ticket_str = obj["Ticket"]
                if ',' in ticket_str:
                    ticket_parts = ticket_str.split(',')
                    return ticket_parts[0] + ticket_parts[5][-5:]
        return no_ticket_value

    def from_object(obj):
        if "Ticket" in obj:
            return ""

        o = ""
        names = [name for name in obj]
        names.sort()

        for value in names:
            o += from_object_inner(obj.get(value))

        return o

    return hashlib.sha1(f"{from_array(arguments)}{salt}{get_ticket_value(arguments)}".encode()).hexdigest()

def invoke_method(server: str, method: str, params: list, session: str) -> tuple[int, any]:
    """
    Invoke a method on the MSP API
    """

    if server.lower() == "uk":
        server = "gb"
    
    req = remoting.Request(target=method, body=params)
    event = remoting.Envelope(AMF3)
    event.headers = remoting.HeaderCollection({
        ("sessionID", False, get_session_id()),
        ("needClassName", False, False),
        ("id", False, calculate_checksum(params))
    })

    event['/1'] = req
    encoded_req = remoting.encode(event).getvalue()
        
    full_endpoint = f"https://ws-{server}.mspapis.com/Gateway.aspx?method={method}"
  
    headers = {
        "content-type": "application/x-amf",
        "x-flash-version": "32,0,0,170",
        "accept-language": "en-us",
        "user-agent": "Mozilla/5.0 (Macintosh; U; Intel Mac OS X; en) AppleWebKit/533.19.4 (KHTML, like Gecko) AdobeAIR/32.0",
        'Connection': 'keep-alive'
    }

    response = requests.post(
        full_endpoint,
        impersonate="chrome",
        headers=headers,
        data=encoded_req,
        timeout=60
    )
        
    if response.status_code != 200:
        return (response.status_code, response.content)
    
    return (response.status_code, remoting.decode(response.content)["/1"].body)

def get_session_id() -> str:
    """
    Generate a random session id
    """
    return base64.b64encode(token_hex(23).encode()).decode()