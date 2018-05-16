#coding:utf-8

import os
from sanic import Sanic
from sanic.response import text

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
    return text('Hello v1')

# for test
@app.websocket('/ws')
async def ws(request, ws):
    async def cf_send(ws):
        i = 0
        while True:
            try:
                await ws.send(bytes([48+i]))
                i += 1
                await asyncio.sleep(1)
            except Exception:
                print('eeeeeeeee2')
    
    async def cf_recv(ws):
        while True:
            try:
                await ws.recv()
            except Exception:
                print('eeeeeeeee3')
    
    fs = [cf_send(ws), cf_recv(ws)]
    try:
        await asyncio.wait(fs)
    except Exception:
        print('eeeeeeeee1')

# end for test

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
