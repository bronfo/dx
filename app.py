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
    return text('Hello v10')


# for test
@app.websocket('/ws')
async def ws(request, ws):
    async def cf_send(ws):
        #i = 0
        while True:
            try:
                d = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                d = b's ' + bytes(d, 'utf-8')
                d = utils.make_chunk(d, KEY)
                await ws.send(d)
                #i += 1
                await asyncio.sleep(1)
            except Exception as e2:
                print('eeeeeeeee2 %s' % e2)
                break
    
    def on_data(d):
        d = utils.crypt_string(d, KEY, False)
        print(d)
    async def cf_recv(ws):
        size = -1
        buf = b''
        while True:
            try:
                d = await ws.recv()
                if type(d) == bytes:
                    buf += d
                    if size == -1:
                        if len(buf) >= 4:
                            size = int.from_bytes(buf[:4], 'big')
                            buf = buf[4:]
                    if size != -1 and len(buf) >= size:
                        on_data(buf[:size])
                        buf = buf[size:]
                        size = -1
                else:
                    raise(Exception('unexcept str'))
            except Exception as e3:
                print('eeeeeeeee3 %s' % e3)
                break
    
    fs = [cf_send(ws), cf_recv(ws)]
    try:
        await asyncio.wait(fs)
    except Exception as e1:
        print('eeeeeeeee1 %s' % e1)

# end for test

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
