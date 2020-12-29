#! /usr/bin/env python

import struct
import threading
import socket
import time
import asyncio
import websockets
import json
import construct
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
        self.tx_file.write("[" + str(time.time()) + "]" + data + "\n")
        self.tx_file.flush()

    def parse_packet(self, data):
        packet = {}
        fmt_header = '<iBBBBBB' # The list of nodes must be computed
        fmt_hk = '<IBBBH'#IBHBBBHHBff'#HH'
        header_items = struct.unpack(fmt_header, data[: struct.calcsize(fmt_header)])
        packet["timestamp"] = time.time()
        packet["rssi"] = header_items[0]
        packet["gs_id"] = Configuration.gs_id
        # FossaSat header
        packet["callsign"] = header_items[1]
        packet["functionId"] = header_items[2]
        packet["frame_len"] = header_items[3]
        packet["src"] = header_items[4]
        packet["dst"] = header_items[5]
        nodes = header_items[len(header_items) - 1]
        route = struct.unpack('B' * nodes, data[struct.calcsize(fmt_header) : struct.calcsize(fmt_header) + nodes])
        packet["route"] = route
        format = construct.Struct(
            "timestamp" / construct.Int32ub,
            "id" / construct.Int8ub,
            "batt_v" / construct.Int8ub,
            "batt_ch_i" / construct.Int8ub,
            "batt_ch_v" / construct.Int16ub,
            "boot_counter" / construct.Int32ub,
            "conf_byte" / construct.Int8ub,
            "rst_counter" / construct.Int16ub,
            "cell_a_v" / construct.Int8ub,
            "cell_b_v" / construct.Int8ub,
            "cell_c_v" / construct.Int8ub,
            "batt_temp" / construct.Int16ub,
            "board_temp" / construct.Int16ub,
            "mcu_temp" / construct.Int8ub,
            "latitude" / construct.Float32b,
            "longitude" / construct.Float32b,
            "tx_counter" / construct.Int16ub,
            "rx_counter" / construct.Int16ub
        )
        packet["telemetry"] =  {}
        container = format.parse(data[struct.calcsize(fmt_header) + nodes : len(data)])
        packet["telemetry"]["timestamp"] = container.timestamp
        packet["telemetry"]["id"] = container.id
        packet["telemetry"]["batt_v"] = container.batt_v
        packet["telemetry"]["batt_ch_i"] = container.batt_ch_i
        packet["telemetry"]["batt_ch_v"] = container.batt_ch_v
        packet["telemetry"]["boot_counter"] = container.boot_counter
        packet["telemetry"]["conf_byte"] = container.conf_byte
        packet["telemetry"]["rst_counter"] = container.rst_counter
        packet["telemetry"]["cell_a_v"] = container.cell_a_v
        packet["telemetry"]["cell_b_v"] = container.cell_b_v
        packet["telemetry"]["cell_c_v"] = container.cell_c_v
        packet["telemetry"]["batt_temp"] = container.batt_temp
        packet["telemetry"]["board_temp"] = container.board_temp
        packet["telemetry"]["mcu_temp"] = container.mcu_temp
        packet["telemetry"]["latitude"] = container.latitude
        packet["telemetry"]["longitude"] = container.longitude
        packet["telemetry"]["tx_counter"] = container.tx_counter
        packet["telemetry"]["rx_counter"] = container.rx_counter
        return json.dumps(packet)

    async def run(self):
        # Access the main loop
        self.running = True
        while(self.running == True):
            # Check if something is received in the buffer
            if(self.input_buffer.available() > 0):
                print("Received something to be send")
                data = self.input_buffer.read()
                async with websockets.connect("ws://localhost:8765/pub") as websocket:
                    self.tx_client = websocket
                    await self.send_socket(self.parse_packet(data))
            # release the cpu
            time.sleep(0.001)
        self.close_log_files()
