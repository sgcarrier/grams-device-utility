import random
import logging
import socket
import struct
import sys
import ctypes, ctypes.util
from ctypes import *

_logger = logging.getLogger(__name__)

class AXIDMA:

    def __init__(self):
        try:
            self.clib = ctypes.CDLL("/usr/lib/dma-consumer.so")
        except Exception as e:
            _logger.error("Could not load DMA shared library with error :")
            _logger.error(e)

    def test_multicast(self):
        self.clib.test_multicast(0x0)

    def start_data_acquisition(self, maxSamples=0, maxTime=0):
        _logger.info("Starting acquisition with multicast")
        acqId = random.randint(1, 65535)

        #The following line is blocking
        ret = self.clib.start_acquisition_multicast(c_int(maxSamples), c_int(maxTime), c_int(acqId))

        if ret != 0:
            _logger.error("Acquisition ended with an error...")

    def stop_data_acquisition(self):
        self.clib.stop_acquisition()
        _logger.info("Stopped acquisition")


    def set_meta_data(self, path, acqID, format, attributes=None):

        message = "ACQ_ID:"+str(acqID)+",PATH:"+path+",FORMAT:"+str(format)+",END:#!"
        multicast_group = ('238.0.0.8', 19001)

        # Create the datagram socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        ttl = struct.pack('b', 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

        sock.sendto(message, multicast_group)

        sock.close()