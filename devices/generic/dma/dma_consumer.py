import time
import smbus
import logging
import ctypes, ctypes.util

_logger = logging.getLogger(__name__)

class AXIDMA:

    def __init__(self):
        try:
            self.clib = ctypes.CDLL("/usr/lib/dma-consumer.so")
        except Exception as e:
            _logger.error("Could not load DMA shared library with error :")
            _logger.error(e)

    def test_multicast(self):
		self.clib.test_multicast(0x12345678)

    def start_data_acquisition(self):
        pass

    def stop_data_acquisition(self):
        pass
