#coding:utf-8

import os
import datetime
import asyncio
from sanic import Sanic
from sanic.response import text
import utils

import logging
logging.basicConfig(format='%(asctime)s %(filename)s %(lineno)s: %(message)s')
logger = logging.getLogger(os.path.basename(__file__))
logger.setLevel(logging.ERROR)

import websockets
websockets.protocol.logger.setLevel(logging.ERROR)

BUFSZ = 4096
KEY = b'mykey'
CMD_PREFIX = b'yb@cui_sf73G84mvc98y#X'
CMD_CONNECT = CMD_PREFIX + b'c'
CMD_CONNECT_OK = CMD_PREFIX + b'0'
CMD_CONNECT_FALSE = CMD_PREFIX + b'1'

app = Sanic()
app.static('/static', 'static')

@app.route("/upload", methods=['POST'])
async def upload(request):
    print(request.files['test'][0].name)
    f = open(request.files['test'][0].name, "wb")
    f.write(request.files['test'][0].body)
    f.close()

    return text("ok")

@app.route("/")
async def index(request):
    return text('Hello v14')


@app.websocket('/ws')
async def ws(request, ws):
    while True:
        d = await ws.recv()
        d = utils.crypt_string(d, KEY, False)
        if type(d) == bytes and d.startswith(CMD_CONNECT):
            logger.error(d[len(CMD_CONNECT):])
            w = None
            try:
                host, port = d[len(CMD_CONNECT):].split(b':')
                r, w = await asyncio.open_connection(host, int(port))
            except Exception:
                logger.error('connect error')
            if w != None:
                d = utils.crypt_string(CMD_CONNECT_OK, KEY, True)
                await ws.send(d)
                
                # exchange
                await utils.exchange(ws, r, w)
            else:
                d = utils.crypt_string(CMD_CONNECT_FALSE, KEY, True)
                await ws.send(d)
                logger.error('connect fail')
        else:
            logger.error('ws unexpected')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
