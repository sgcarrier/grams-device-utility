import random
import logging
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
