import logging
from periphery import GPIO

_logger = logging.getLogger(__name__)


class MUX:
    DEVICE_NAME = "MUX"
    GPIO_PINS = {}

    def __init__(self, gpio_pins=None, name="MUX"):
        self._name = name
        self.__dict__ = {}
        if gpio_pins and isinstance(gpio_pins, dict):
            self.GPIO_PINS = gpio_pins
            self._PIN_CONFIG = [0] * len(gpio_pins)
        else:
            self._PIN_CONFIG = []
        self.from_dict_plat()


    def from_dict_plat(self):
        for key, value in self.REGISTERS_INFO.items():
            value = Command(value, str(key), self)
            self.__dict__[key] = value

    def register_pin(self, name, pinNum):
        self.GPIO_PINS[name] = pinNum

    def __repr__(self):
        return self._name

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]

    def selftest(self, muxName):
        # mux is write-only, skip self-test
        return 0

    def readout_all_registers(self, muxName):
        _logger.info("==== Device report ====")
        _logger.warning("MUX is write-only, skipping...")
        return 0

    def gpio_set(self, name, value):
        if not self.GPIO_PINS:
            _logger.warning("No gpio pins defined. Aborting...")
            return -1

        if name in self.GPIO_PINS:
            pin = self.GPIO_PINS[name]
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
            if len(args) == 1:
                return self._acc.gpio_set(self._name, args[0])
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