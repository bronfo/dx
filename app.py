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
    return text('Hello v11')


# for test
@app.websocket('/ws')
async def ws(request, ws):
    while True:
        d = await ws.recv()
        d = utils.crypt_string(d, KEY, False)
        logger.error(d)
        if d == CMD_CONNECT:
            # todo do connect
            d = utils.crypt_string(CMD_CONNECT_OK, KEY, True)
            await ws.send(d)
            logger.error('CMD_CONNECT_OK')
            break

# end for test

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
