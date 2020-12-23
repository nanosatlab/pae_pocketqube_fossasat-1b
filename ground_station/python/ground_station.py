#! /usr/bin/env python

import signal
import time
import sys
import asyncio
import struct
from Configuration import Configuration
from RadioManager import RadioManager
from SocketManager import SocketManager

def stop(signal_received, frame):
    global running
    running = False

def test_send_from_radio_to_LoRa(signal_received, frame):
    global port
    #radio_manager.input_buffer.write("hola".encode('utf-8'))
    radio_manager.input_buffer.write(bytearray(254))

def test_send_from_LoRa_to_inet(signal_received, frame):
    global port
    socket_manager.input_buffer.write("hola".encode('utf-8'))

def reset_files(signal_received, frame):
    global radio_manager
    global socket_manager
    radio_manager.reset_log_files()
    socket_manager.reset_log_files()

def main():
    global running
    global radio_manager
    global socket_manager

    # Create threads
    try:
        radio_manager = RadioManager()
    except Exception as e:
        print("[ERROR] Serial port " + Configuration.serial_port + ": " + str(e))
        print("Exit the software")
        exit(-1)
    socket_manager = SocketManager()
    # Assign buffers
    radio_manager.set_output_buffer(socket_manager.input_buffer)
    socket_manager.set_output_buffer(radio_manager.input_buffer)
    # Start threads
    radio_manager.start()
    asyncio.get_event_loop().run_until_complete(socket_manager.run())
    # Access the main loop
    running = True
    while(running == True):
        # release the cpu
        time.sleep(1)
    # Close properly the threads
    #if(socket_manager.is_alive() == True):
    #    socket_manager.stop()
    if(radio_manager.is_alive() == True):
        radio_manager.stop()
    time.sleep(0.3)
    exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, test_send_from_LoRa_to_inet)
    signal.signal(signal.SIGQUIT, stop)
    main()

