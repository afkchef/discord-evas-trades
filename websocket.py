import websocket #pip install websocket-client
import json
import threading
import time

def send_json_request(ws, request):
    ws.send(json.dumps(request))

def recieve_json_response(ws):
    response = ws.recv()
    if response:
        return json.loads(response)

def heartbeat(interval, ws):
    print('Heartbeat Begin')
    while True:
        time.sleep(interval)
        heartbeatJSON = {
            "op": 1,
            "d": "null"
        }
        send_json_request(ws, heartbeatJSON)
        print("Heartbeat sent")

ws = websocket.WebSocket()
ws.connect('wss://gateway.discord.gg/?v=6&encording=json')
event = recieve_json_response(ws)

heartbeat_interval = event['d']['heartbeat_interval'] /1000
threading._start_new_thread(heartbeat, (heartbeat_interval,ws))

token = "MTYwMTk1ODQwMTczMDE1MDQw.GZRGP1._fcAcCRs3hLvZ49Fb1h-_xwqZGeSMKmQh9nCFw"
payload = {
    'op': 2,
    'd':{
        "token": token,
        "guild_id": "804806639168651274",
        "properties": {
            "$os":"macOS",
            "$browser": "chrome",
            "$device": "pc"
        }
    }
}

send_json_request(ws, payload)

while True:
    event = recieve_json_response(ws)
    try:
        print(f"{event['d']['author']['username']}: {event['d']['content']}")
        op_code = event('op')
        if op_code == 11:
            print('heartbeat rcvd')
    except:
        pass

#options id: 804806639168651274
#evapands id: 1022585814183575603