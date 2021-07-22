import time
import smbus
import logging
from periphery import GPIO

_logger = logging.getLogger(__name__)

class GEN_GPIO:

    DEVICE_NAME = "GEN_GPIO"
    GPIO_PINS = {}

    ADDRESS_INFO = []



    def __init__(self, name="GEN_GPIO", accessor=None):
        self.__dict__ = {}
        self._name = name
        #self.from_dict_plat()

    # def from_dict_plat(self):
    #     for key, value in self.REGISTERS_INFO.items():
    #         value = Command(value, str(key), self)
    #         self.__dict__[key] = value

    def device_summary(self):
        report = ('{DeviceName: <10} :: N/A\n'.format(DeviceName=self._name))
        return report

    def __repr__(self):
        return self._name

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]

    def selftest(self, devNum):
        # No selftests to be done, skipping
        return 1



    def gpio_set(self, name, value):
        if not self.GPIO_PINS:
            _logger.warning("No gpio pins defined. Aborting...")
            return -1

        if name in self.GPIO_PINS[0]:
            pin = self.GPIO_PINS[0][name]
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
                self._acc.write_param(args[0], self._name, args[1])
            elif len(args) == 1:
                return self._acc.read_param(args[0], self._name)
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