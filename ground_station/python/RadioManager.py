#! /usr/bin/env python

import sys
import kiss
import time
import serial
import threading
import time
from datetime import datetime
from SyncBuffer import SyncBuffer
from Configuration import Configuration

class RadioManager(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.input_buffer = SyncBuffer(Configuration.max_size_radio)
        self.port = kiss.Kiss(Configuration.serial_port,
            Configuration.serial_speed,
            Configuration.serial_bytesize,
            Configuration.serial_parity,
            Configuration.serial_stopbits,
            Configuration.serial_timeout)
        print("Serial port " + Configuration.serial_port + " opened with: {" +
            str(Configuration.serial_speed) + "}")
        self.create_log_files()

    # private access
    def create_log_files(self):
        now = datetime.now()
        self.tx_file = open(Configuration.log_folder + "/" + Configuration.tx_lora_log_file + "_" + now.strftime("%Y_%m_%d_%H_%M_%S"), "w")
        self.rx_file = open(Configuration.log_folder + "/" + Configuration.rx_lora_log_file + "_" + now.strftime("%Y_%m_%d_%H_%M_%S"), "w")
        self.log = open(Configuration.log_folder + "/log_" + now.strftime("%Y_%m_%d_%H_%M_%S"), "w")
        self.log.write("This is the log file in which raw information is printed\n")

    # private access
    def close_log_files(self):
        self.tx_file.close()
        self.rx_file.close()
        self.log.close()

    # public access
    def reset_log_files(self):
        self.close_log_files()
        self.create_log_files()
        print("Files reseted")

    # public access
    def set_output_buffer(self, buffer):
        self.output_buffer = buffer

    # public access
    def is_connected(self):
        return self.port.is_open

    # public access
    def stop(self):
        self.running = False

    # called privately
    def read_radio(self):
        data = self.port.read()
        if(len(data) > 0):
            self.log.write("From Lora size: " + str(len(data)) + "\n")
            self.log.flush()
            # Return the received data
            self.rx_file.write("[" + str(time.time()) + "]" + data.hex() + "\n")
            self.rx_file.flush()
            return data
        return b''

    # called privately
    def write_radio(self, data):
        self.port.write(data)
        self.tx_file.write("[" + str(time.time()) + "]" + data.hex() + "\n")
        self.tx_file.flush()

    def run(self):
        # Access the main loop
        self.running = True
        while(self.running == True):
            # Check if something is received in the buffer
            if(self.input_buffer.available() > 0):
                data = self.input_buffer.read()
                self.log.write("============ FROM INTERNET ============\n");
                self.log.write("[" + str(time.time()) + "] Received " + str(len(data)) + " bytes\n");
                self.log.write("Packet: " + str(data.hex()) + "\n")
                self.log.flush()
                self.write_radio(data)
            # Check if something is received from the radio
            data = self.read_radio()
            if(len(data) > 0):
                self.log.write("============ FROM LORA ============\n")
                self.log.write("[" + str(time.time()) + "] Received " + str(len(data)) + " bytes\n")
                self.log.write("Packet: " + str(data.hex()) + "\n")
                self.log.flush()
                self.output_buffer.write(data)
            # release the cpu
            time.sleep(0.001)
        self.close_log_files()
