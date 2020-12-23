#! /usr/bin/env python

import struct
import threading
import socket
import time
import asyncio
import websockets
from datetime import datetime
from Configuration import Configuration
from SyncBuffer import SyncBuffer

current_milli_time = lambda: int(round(time.time() * 1000))

class SocketManager:

    def __init__(self):
        # Open the server
        self.connected = False
        self.input_buffer = SyncBuffer(Configuration.max_size_inet)
        self.create_log_files()

    # private access
    def create_log_files(self):
        now = datetime.now()
        self.tx_file = open(Configuration.log_folder + "/" + Configuration.tx_inet_log_file + "_" + now.strftime("%Y_%m_%d_%H_%M_%S"), "w")

    # private access
    def close_log_files(self):
        self.tx_file.close()

    # public access
    def reset_log_files(self):
        self.close_log_files()
        self.create_log_files()
        print("Files reseted")

    # public access
    def is_connected(self):
        return self.connected

    # public access
    def stop(self):
        self.running = False

    # public access
    def set_output_buffer(self, buffer):
        self.output_buffer = buffer

    # called privately
    async def send_socket(self, data):
        await self.tx_client.send(data)
        self.tx_file.write("[" + str(time.time()) + "]" + data.hex() + "\n")
        self.tx_file.flush()

    def parse_packet(data):
        packet = {}
        packet["timestamp"] = time.time()
        packet["gs_id"] = Configuration.gs_id
        fmt_header = 'iBBB' # The list of nodes must be computed
        fmt_hk = 'IBBBHIBHBBBHHBiiHH'
        header_items = struct.unpack(fmt_header, data[: struct.calcsize(fmt_header)])
        packet["rssi"] = header_items[0]
        packet["source"] = header_items[1]
        packet["destination"] = header_items[2]
        nodes = header_items[len(header_items) - 1]
        route = struct.unpack('B' * nodes, data[struct.calcsize(fmt_header) : struct.calcsize(fmt_header) + nodes])
        packet["route"] = route
        hk_items = struct.unpack(fmt_hk, data[struct.calcsize(fmt_header) + nodes : len(data)])
        packet["telemetry"] = {}
        packet["telemetry"]["timestamp"] = hk_items[0]
        packet["telemetry"]["id"] = hk_items[1]
        packet["telemetry"]["batt_v"] = hk_items[2]
        packet["telemetry"]["batt_ch_i"] = hk_items[3]
        packet["telemetry"]["batt_ch_v"] = hk_items[4]
        packet["telemetry"]["boot_counter"] = hk_items[5]
        packet["telemetry"]["rst_counter"] = hk_items[6]
        packet["telemetry"]["conf_byte"] = hk_items[7]
        packet["telemetry"]["cell_a_v"] = hk_items[8]
        packet["telemetry"]["cell_b_v"] = hk_items[9]
        packet["telemetry"]["cell_c_v"] = hk_items[10]
        packet["telemetry"]["batt_temp"] = hk_items[11]
        packet["telemetry"]["board_temp"] = hk_items[12]
        packet["telemetry"]["mcu_temp"] = hk_items[13]
        packet["telemetry"]["latitude"] = hk_items[14]
        packet["telemetry"]["longitude"] = hk_items[15]
        packet["telemetry"]["tx_counter"] = hk_items[16]
        packet["telemetry"]["rx_counter"] = hk_items[17]
        return packet

    async def run(self):
        # Access the main loop
        self.running = True
        while(self.running == True):
            # Check if something is received in the buffer
            if(self.input_buffer.available() > 0):
                data = self.input_buffer.read()
                async with websockets.connect("ws://localhost:8765/pub") as websocket:
                    self.tx_client = websocket
                    await self.send_socket(parse_packet(data))
            # release the cpu
            time.sleep(0.001)
        self.close_log_files()
