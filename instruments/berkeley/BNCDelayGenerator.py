import telnetlib
import time
import logging


_logger = logging.getLogger(__name__)

"""
    Control class for the BNC delay generator. Port 4000 is the default for the telnet communication
"""


class BNCDelayGenerator:

    def __init__(self, host, port=4000, encoding='ascii'):
        self._host = host
        self._port = port
        self.tn = None
        self._encoding = encoding

    def start(self):
        self.tn = telnetlib.Telnet(self._host, port=self._port)
        time.sleep(0.5)

    def stop(self):
        self.tn.close()

    def setFreq(self, outputNum, freq):
        if self.tn:
            query = "FREQ F" + str(outputNum) + "," + str(freq) + "\n"
            _logger.debug(query)
            self.tn.write(query.encode(self._encoding))
            time.sleep(0.5)
        else:
            _logger.error("Telnet connection not started. Call the start() function first.")

    def setAmp(self, outputNum, amplitude):
        if self.tn:
            query = "AMPL T" + str(outputNum) + "," + str(amplitude) + "\n"
            _logger.debug(query)
            self.tn.write(query.encode(self._encoding))
            time.sleep(0.5)
        else:
            _logger.error("Telnet connection not started. Call the start() function first.")

    """
        Set the delay of an output in ps. Note: there seems to be an error in the documentation for the BNC telnet 
        command list. The doc says it needs a reference output from which to delay ( DELAY Tout, Tref, delay) but it
        doesn't seem to be true.  
    """
    def setDelay(self, outputNum, delay):
        if self.tn:
            query = "DELAY T" + str(outputNum) + ", " + str(delay) + "\n"
            _logger.debug(query)
            self.tn.write(query.encode(self._encoding))
            time.sleep(0.5)
        else:
            _logger.error("Telnet connection not started. Call the start() function first.")

    def setOn(self, outputNum, trigSource="IN1"):
        if self.tn:
            query = "TRIG T" + str(outputNum) + "," + str(trigSource) + "\n"
            _logger.debug(query)
            self.tn.write(query.encode(self._encoding))
            time.sleep(0.5)
        else:
            _logger.error("Telnet connection not started. Call the start() function first.")

    def setOff(self, outputNum):
        if self.tn:
            query = "TRIG T" + str(outputNum) + ",OFF" + "\n"
            _logger.debug(query)
            self.tn.write(query.encode(self._encoding))
            time.sleep(0.5)
        else:
            _logger.error("Telnet connection not started. Call the start() function first.")

    def testID(self):
        if self.tn:
            query = "*IDN?" + "\n"
            self.tn.write(query.encode(self._encoding))
            print(self.tn.read_all())
            time.sleep(0.5)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    BNC = BNCDelayGenerator(host='192.168.1.253', port=4000)
    #BNC.start()
    BNC.setFreq(1, 500)


