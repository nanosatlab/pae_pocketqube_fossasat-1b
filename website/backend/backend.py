#! /usr/bin/env python
import signal
import asyncio
import websockets
import json
import time

def send_pub(signal_received, frame):
    item = {
        "timestamp": 1608631208,
        "gs_id": "NanoSatLab",
        "rssi": -88.5,
        "callsign": 1,
        "functionId": 2,
        "frame_len": 125,
        "src": 0,
        "dst": 255,
        "route": [1, 2, 3, 4],
        "telemetry": {
            "timestamp": 1608631208,
            "id": 0,
            "batt_v": 3.3,
            "batt_ch_i": 0.0,
            "batt_ch_v": 0.0,
            "boot_counter": 15,
            "rst_counter": 1,
            "conf_byte": 4,
            "cell_a_v": 12.0,
            "cell_b_v": 12.0,
            "cell_c_v": 12.0,
            "batt_temp": 24.5,
            "board_temp": 27.8,
            "mcu_temp": 40.5,
            "latitude": 41.389210362553364,
            "longitude": 2.1125334136449805,
            "tx_counter": 15,
            "rx_counter": 20
        }
    }
    global connections
    if(len(connections) > 0):
        print("Sending packets")
        for ws in connections:
            asyncio.ensure_future(ws.send(json.dumps(item)))
    else:
        print("No connections")

def send_wrong_pub(signal_received, frame):
    global connections
    if(len(connections) > 0):
        print("Sending packets")
        for ws in connections:
            asyncio.ensure_future(ws.send("[ERROR] Wrong message received"))
    else:
        print("No connections")

def close(signal_received, frame):
    global rx_file
    global send_file
    if(rx_file != None):
        rx_file.close()
    if(send_file != None):
        send_file.close()

async def handler(websocket, path):
    global connections
    global rx_file
    if(path == "/sub"):
        i = len(connections)
        connections.append(websocket)
        print("added subscriber #", i)
        try:
            async for msg in websocket:
                pass  # ignore
        except websockets.ConnectionClosed:
            pass
        finally:
            print("removing subscriber #", i)
            connections.remove(websocket)
    elif(path == "/pub"):
        async for msg in websocket:
            print("<", msg)
            for ws in connections:
                asyncio.ensure_future(ws.send(msg))
            rx_file.write("[" + str(time.time()) + "]" + str(msg) + "\n")
            rx_file.flush();
    elif(path == "/all"):
        print("Requested /all")
        send_file = open("./rx_packets", "r")
        for line in send_file.readlines():
            data = line.split("]{")
            if(len(data) > 1):
                data = "{" + data[1]
                asyncio.ensure_future(websocket.send(data))
        send_file.close()


def main():
    # Init the variables
    global connections
    connections = []

    # Upload JSON content
    global rx_file
    rx_file = open("./rx_packets", "a")

    # Launch websocket server
    start_server = websockets.serve(handler, '0.0.0.0', 8765)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
    rx_file.close();
    exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, send_pub)
    main()
