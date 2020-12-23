#! /usr/bin/env python

import serial
import time

KISS_FEND = b'\xc0'
KISS_FESC = b'\xdb'
KISS_TFESC = b'\xdc'
KISS_TFEND = b'\xdd'

current_milli_time = lambda: int(round(time.time() * 1000))

class Kiss:
    def __init__(self, port, speed, bytesize, parity, stopbits, timeout):
        self.port = serial.Serial(port, speed, bytesize, parity, stopbits, timeout)

    def is_open(self):
        return self.port.is_open

    def read(self):
        started_frame = False
        finished_frame = False
        fesc_found = False
        frame = b''
        if(self.port.in_waiting > 0):
            start_time = current_milli_time();
            while(finished_frame == False):
                if(self.port.in_waiting > 0):
                    b = self.port.read()
                    # There is data to process
                    if(b == KISS_FEND and started_frame == False):
                        started_frame = True;
                    elif(b == KISS_FEND and finished_frame == False):
                        finished_frame = True;
                    elif(b == KISS_FESC and fesc_found == False):
                        fesc_found = True;
                    elif(b == KISS_TFEND and fesc_found == True):
                        frame += KISS_FEND
                        fesc_found = False
                    elif(b == KISS_TFESC and fesc_found == True):
                        frame += KISS_FESC
                        fesc_found = False;
                    elif(started_frame == True):
                        frame += b
                elif(current_milli_time() >= start_time + 10):   # waiting 10 ms to receive a byte
                    print("[KISS] Frame started but not finished")
                    return b'';
                time.sleep(0.001)
        return frame;

    def write(self, data):
        # Include first FEND
        frame = KISS_FEND
        # Include content
        for i in range(1, len(data) + 1):
            b = data[i-1:i]
            if(b == KISS_FEND):
                frame += KISS_FESC
                frame += KISS_TFEND
            elif(b == KISS_FESC):
                frame += KISS_FESC
                frame += KISS_TFESC
            else:
                frame += b
        # Close the frame with FEND
        frame += KISS_FEND
        # Send through the UART
        written = self.port.write(frame);
        if(written != len(frame)):
            return False;
        return True;

    def close(self):
        self.port.close()
