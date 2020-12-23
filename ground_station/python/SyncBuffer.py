#! /usr/bin/env python

import threading
import time

class SyncBuffer:

    def __init__(self, max_size = float('inf')):
        self.buffer = []
        self.size = 0    # contains the bytes in the buffer
        self.max_size = max_size
        self.locker = threading.Lock()

    def available(self):
        self.locker.acquire()
        tmp_size = self.size
        self.locker.release()
        return tmp_size

    def write(self, data):
        data_size = len(data)
        self.locker.acquire()
        if(self.size < self.max_size):
            self.buffer.append(data)
            self.size += data_size
            tmp_size = data_size
        else:
            tmp_size = 0
        self.locker.release()
        return tmp_size

    def read(self):
        self.locker.acquire()
        tmp_data = b''
        if(self.size > 0):
            tmp_data = self.buffer.pop(0)
            self.size -= len(tmp_data)
        self.locker.release()
        return tmp_data

