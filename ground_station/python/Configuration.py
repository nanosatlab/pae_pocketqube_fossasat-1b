#! /usr/bin/env python

import serial

# configuration parameters
class Configuration:
    remote_host = '10.52.72.10'
    remote_tx_port = 5557              # port of inet socket
    remote_rx_port = 5555              # port of inet socket
    server_timeout = 10             # timeout to connect with the server [seconds]
    recv_timeout = 5 #localhost = 0.01             # Timeout to receive a data from inet socket [seconds]
    max_size_radio = float('inf')   # Maximum input buffer size of the SocketManager
    max_size_inet = float('inf')    # Maximum input buffer size of the SocketManager
    serial_port = "/dev/ttyUSB0"
    serial_speed = 500000 #115200
    serial_bytesize = serial.EIGHTBITS
    serial_parity = serial.PARITY_NONE
    serial_stopbits = serial.STOPBITS_ONE
    serial_timeout = 0.01    # in seconds
    log_folder = "./log/"
    rx_lora_log_file = "rx_lora_log_file"
    tx_lora_log_file = "tx_lora_log_file"
    tx_inet_log_file = "tx_inet_log_file"
    rx_inet_log_file = "rx_inet_log_file"
    gs_id = "NanoSatLab"
