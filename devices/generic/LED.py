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


    def set(self, pinNum, value):
        if not self.GPIO_PINS:
            _logger.warning("No gpio pins defined. Aborting...")
            return -1

        if pinNum < len(self.ADDRESS_INFO):
            pin = self.ADDRESS_INFO[pinNum]
            g = GPIO(pin, "out")
            g.write(value)
            g.close()
        else:
            _logger.error("Could not find pin named " + str(name) + ". Aborting...")
            return -1

        return 0

class Command():
    def __init__(self, d, name="", acc=None):
        self.__dict__ = {}
        self._name = name
        self._acc = acc

    def __call__(self, *args):
        try:
            if len(args) == 2:
                self._acc.set(args[0], args[1])
            elif len(args) == 1:
                return self._acc.get(args[0], self._name)
            else:
                _logger.warning("Incorrect number of arguments. Ignoring")
        except Exception as e:
            _logger.error("Could not set message to device. Check connection...")
            raise e


    def from_dict(self, d, name=""):
        for key, value in d.items():
            self.__dict__[key] = value

    def __repr__(self):
        return self._name

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]