import json

from client import Api

soc_url = 'wss://socket.coinex.com/'

mess = {
    "id": 4,
    "method": "state.subscribe",
    "params": []
}

message = json.dumps(mess).encode('utf-8')
# s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# s.connect((soc_url, 8765))
# s.send(message)
# print(s)
# s.close()

import asyncio
import websockets

coinex = Api()
data = {'access_id': coinex.access_id, 'tonce': coinex.ts}
sign = coinex._sign(data)

auth_soc = {
    "method": "server.sign",
    "params": [
        coinex.access_id,
        sign,
        coinex.ts
    ],
    "id": 15,
}

subscribe_soc = {
    "method": "depth.subscribe",
    "params": ["EMCUSDT", 1, '0'],
    "id": 114775
}

orders_soc = {
  "method": "order.account_query",
  "params": [0, "EMCUSDT", 0, 0, 10],
  "id": 65744
}


async def pinger(websocket):
    ping_soc = {
        "method": "server.ping",
        "params": [],
        "id": 11
    }
    await asyncio.sleep(2)
    await websocket.send(json.dumps(ping_soc).encode('utf-8'))


async def connect_soc():
    async with websockets.connect(soc_url, ping_interval=10, ping_timeout=None) as websocket:
        # await websocket.send(message)
        # print(f"> {message}")
        # greeting = await websocket.recv()
        # print(f"< {greeting}")
        await websocket.send(json.dumps(auth_soc).encode('utf-8'))
        await pinger(websocket)
        print('try sign')
        await websocket.recv()
        # print('result of auth', res)
        await websocket.send(json.dumps(subscribe_soc).encode('utf-8'))
        await websocket.send(json.dumps(orders_soc).encode('utf-8'))
        cnt = 0
        async for msg in websocket:
            print(msg)
            await pinger(websocket)

        # while True:
        #     res = await asyncio.wait_for(websocket.recv(), timeout=10)
        #     print(res)
        #     if cnt > 5:
        #         print('cnt = 5')
        #         await websocket.ping()
        #         cnt = 0
        #     cnt += 1
        #     # await pinger(websocket)


async def main_loop():
    try:
        await connect_soc()
    except Exception as e:
        print(e)
        return


asyncio.get_event_loop().run_until_complete(main_loop())
# asyncio.get_event_loop().run_forever()