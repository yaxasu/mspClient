"""
A Python implementation to interact with the MSP API
"""

import hashlib
import binascii
from curl_cffi import requests
import random
import base64
from datetime import date
from pyamf import remoting, ASObject, AMF3, amf3
from secrets import token_hex

def _marking_id():
    """Generator for marking IDs."""
    _int = random.randint(1, 100)
    while True:
        _int += random.randint(1, 2)
        yield _int

# Instantiate the generator
marking_id = _marking_id()

def ticket_header(ticket: str) -> ASObject:
    """
    Generate a ticket header for the given ticket.
    """
    loc1bytes = str(next(marking_id)).encode('utf-8')
    loc5 = hashlib.md5(loc1bytes).hexdigest()
    loc6 = binascii.hexlify(loc1bytes).decode()
    return ASObject({"Ticket": ticket + loc5 + loc6, "anyAttribute": None})

def calculate_checksum(arguments):
    """
    Calculate the checksum for the given arguments.
    """
    no_ticket_value = "XSV7%!5!AX2L8@vn"
    salt = "2zKzokBI4^26#oi"

    def from_array(arguments):
        return ''.join(from_object_inner(i) for i in arguments)

    def from_object_inner(obj):
        if obj is None:
            return ""
        if isinstance(obj, (int, str, bool)):
            return str(obj)
        if isinstance(obj, bytes):
            return from_byte_array(obj)
        if isinstance(obj, list):
            return from_array(obj)
        if isinstance(obj, dict):
            return from_object(obj)
        if isinstance(obj, date):
            return f"{obj.year}{obj.month - 1}{obj.day}"
        if isinstance(obj, amf3.ByteArray):
            return from_byte_array(obj)
        if isinstance(obj, ASObject):
            return from_object(obj)
        return ""

    def from_byte_array(bytes_obj):
        if len(bytes_obj) <= 20:
            return bytes_obj.getvalue().hex()

        num = len(bytes_obj) // 20
        array = bytearray(20)
        for i in range(20):
            bytes_obj.seek(num * i)
            array[i] = bytes_obj.read(1)[0]

        return array.hex()

    def get_ticket_value(arr):
        for obj in arr:
            if isinstance(obj, ASObject) and "Ticket" in obj:
                ticket_str = obj["Ticket"]
                ticket_parts = ticket_str.split(',')
                return ticket_parts[0] + ticket_parts[5][-5:] if ',' in ticket_str else ticket_str
        return no_ticket_value

    def from_object(obj):
        if "Ticket" in obj:
            return ""

        names = sorted(obj.keys())
        return ''.join(from_object_inner(obj[name]) for name in names)

    return hashlib.sha1(f"{from_array(arguments)}{salt}{get_ticket_value(arguments)}".encode()).hexdigest()

def invoke_method(server: str, method: str, params: list, session: str) -> tuple[int, any]:
    """
    Invoke a method on the MSP API.
    """
    server = "gb" if server.lower() == "uk" else server

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
        return response.status_code, response.content
    
    return response.status_code, remoting.decode(response.content)["/1"].body

def get_session_id() -> str:
    """
    Generate a random session ID.
    """
    return base64.b64encode(token_hex(23).encode()).decode()
