#coding:utf-8

import sys
import asyncio

# bytes data
def crypt_string(data, key, encode=True):
    from itertools import cycle
    import base64
    # the python3
    izip = zip
    # to bytes
    #data = data.encode()
    if not encode:
        data = base64.b64decode(data)
    #xored = ''.join(chr(ord(x) ^ ord(y)) for (x,y) in izip(data, cycle(key)))
    xored = b''.join(bytes([x ^ y]) for (x,y) in izip(data, cycle(key)))
    return base64.b64encode(xored) if encode else xored

def make_chunk(data, key):
    data = crypt_string(data, key, True)
    return int.to_bytes(len(data), 4, 'big') + data
