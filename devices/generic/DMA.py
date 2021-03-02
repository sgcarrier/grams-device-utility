import random
import logging
import socket
import struct
import sys
import ctypes, ctypes.util
from ctypes import *

_logger = logging.getLogger(__name__)

class DMA:

    def __init__(self):
        try:
            self.clib = ctypes.CDLL("/usr/lib/dma-consumer.so")
        except Exception as e:
            _logger.error("Could not load DMA shared library with error :")
            _logger.error(e)

    def test_multicast(self):
        self.clib.test_multicast(0x0)

    def start_data_acquisition(self, acqId, maxSamples=-1, maxTime=-1, minimumBuffer=0):
        _logger.info("Starting acquisition with multicast")

        #The following line is blocking
        ret = self.clib.start_acquisition_multicast(c_int(maxSamples), c_int(maxTime), c_int(acqId), c_int(minimumBuffer))

        if ret != 0:
            _logger.error("Acquisition ended with an error...")

    def stop_data_acquisition(self):
        self.clib.stop_acquisition()
        _logger.info("Stopped acquisition")


    def set_meta_data(self, path, acqID, format, attributes=None):
        message_bytes = str.encode("ACQ_ID:") + acqID.to_bytes(4, 'little') + str.encode(",PATH:" + path + ",FORMAT:") + format.to_bytes(4, 'little') + str.encode(",END:#!")
        multicast_group = ('238.0.0.8', 19001)

        # Create the datagram socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        ttl = struct.pack('b', 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

        sock.sendto(message_bytes, multicast_group)

        sock.close()

    def test_data(self, acqID):

        message_pre = "SRC:CHARTIER/ASIC0,LEN:32,ACQ_ID:"
        message_id = acqID.to_bytes(4, 'little')
        message_data = ",DATA:"
        message_end = ",END:#!"
        data = (0xAAAAAAAAAAAAAAAA).to_bytes(8, 'little') + (0x0000000000000002).to_bytes(8, 'little') + (0x1234567887654321).to_bytes(8, 'little') + (0xAAAAAAABAAAAAAAB).to_bytes(8, 'little')
        message_bytes = str.encode(message_pre) + message_id + str.encode(message_data) + data + str.encode(message_end)
        multicast_group = ('238.0.0.8', 19002)

        # Create the datagram socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        ttl = struct.pack('b', 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

        sock.sendto(message_bytes, multicast_group)

        sock.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    dma = DMA()

    dma.set_meta_data("test/path/hope/despair", acqID=1234, format=1)

    dma.test_data(1234)
