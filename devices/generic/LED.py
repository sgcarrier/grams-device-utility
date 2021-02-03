import time
import smbus
import logging
from periphery import GPIO

_logger = logging.getLogger(__name__)

class LED:

    DEVICE_NAME = "LED"

    DEVICE_TYPE = "GPIO"

    ADDRESS_INFO = []
    GPIO_PINS = {}


    def __init__(self, name="LED"):
        self.__dict__ = {}
        self._name = name

    def device_summary(self):
        report = ('{DeviceName: <10} :: N/A\n'.format(DeviceName=self._name))
        return report

    def __call__(self, *args):
        try:
            if len(args) == 2:
                self.set(args[0], args[1])
            else:
                _logger.warning("Incorrect number of arguments. Ignoring")
        except Exception as e:
            _logger.error("Could not set message to device. Check connection...")
            raise e


    def __repr__(self):
        return self._name

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]

    def selftest(self, devNum):
        # No selftests to be done, skipping
        return 1

    def set(self, pinName, value):
        if not self.GPIO_PINS:
            _logger.warning("No gpio pins defined. Aborting...")
            return -1


            #g = GPIO(pinNum, "out")
        if pinName in self.GPIO_PINS[0]:
            pinNum = self.GPIO_PINS[0][pinName]

            try:
                g = GPIO(pinNum, "out")
                g.write(value)
                g.close()
            except Exception as e:
                _logger.error("Failed to access pin " + str(pinName) + " with the following error:")
                _logger.error(e)
        else:
            _logger.error("Could not find pin " + str(pinName) + ". Aborting...")
            return -1

        return 0

