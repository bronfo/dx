#coding:utf-8

import sys
import asyncio

import logging, os
logging.basicConfig(format='%(asctime)s: %(message)s')
logger = logging.getLogger(os.path.basename(__file__))
logger.setLevel(logging.DEBUG)

BUFSZ = 4096
KEY = b'mykey'
CMD_PREFIX = b'yb@cui_sf73G84mvc98y#X'
CMD_CONNECT = CMD_PREFIX + b'c'
CMD_CONNECT_OK = CMD_PREFIX + b'0'
CMD_CONNECT_FALSE = CMD_PREFIX + b'1'
CMD_CLOSE = CMD_PREFIX + b'x'
CMD_CLOSE_RESP = CMD_PREFIX + b'x0'

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

# exchange payload
async def exchange(ws, r, w):
    t1 = asyncio.Task(ws.recv())
    t2 = asyncio.Task(r.read(BUFSZ))
    pending = [t1, t2]
    ws_recv_close_cmd = False
    ws_send_close_cmd = False
    ws_recv_close_resp = False
    peer_close = False
    while True:
        done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
        if t1 in done:
            msg = t1.result()
            if not msg:
                raise Exception('ws close?')
            msg = crypt_string(msg, KEY, False)
            if msg == CMD_CLOSE:
                ws_recv_close_cmd = True
                await ws.send(crypt_string(CMD_CLOSE_RESP, KEY, True))
                if not ws_send_close_cmd:
                    ws_send_close_cmd = True
                    await ws.send(crypt_string(CMD_CLOSE, KEY, True))
                if not peer_close:
                    w.close()
                if ws_recv_close_resp and peer_close:
                    logger.info('break1')
                    break
            elif msg == CMD_CLOSE_RESP:
                ws_recv_close_resp = True
                if ws_recv_close_cmd and peer_close:
                    logger.info('break2')
                    break
            else:
                w.write(msg)
            
            t1 = asyncio.Task(ws.recv())
            pending.add(t1)
        if t2 in done:
            data = t2.result()
            if data:
                data = crypt_string(data, KEY, True)
                await ws.send(data)
                
                t2 = asyncio.Task(r.read(BUFSZ))
                pending.add(t2)
            else:
                peer_close = True
                if not ws_send_close_cmd:
                    ws_send_close_cmd = True
                    await ws.send(crypt_string(CMD_CLOSE, KEY, True))
                elif ws_recv_close_resp and ws_recv_close_cmd:
                    logger.info('break3')
                    break
