import time
import logging
from periphery import SPI, GPIO

_logger = logging.getLogger(__name__)

class LMK01020:

    DEVICE_NAME = "LMK01020"

    #All register info concerning all LMK parameters
    REGISTERS_INFO = {
        #  if min=max=0, read-only, min=max=1 Self-clearing)
                   "RESET": { "addr":  0, "loc": 31, "mask": 0x80000000, "min": 0, "max":   1},  # RESET,
             "CLKOUT0_MUX": { "addr":  0, "loc": 17, "mask":    0x60000, "min": 0, "max":   3},  #CLKOUT0_MUX,
              "CLKOUT0_EN": { "addr":  0, "loc": 16, "mask":    0x10000, "min": 0, "max":   1},  #CLKOUT0_EN,
             "CLKOUT0_DIV": { "addr":  0, "loc":  8, "mask":     0xFF00, "min": 0, "max": 255},  #CLKOUT0_DIV,
             "CLKOUT0_DLY": { "addr":  0, "loc":  4, "mask":       0xF0, "min": 0, "max":  15},  #CLKOUT0_DLY,

             "CLKOUT1_MUX": { "addr":  1, "loc": 17, "mask":    0x60000, "min": 0, "max":   3},  #CLKOUT1_MUX,
              "CLKOUT1_EN": { "addr":  1, "loc": 16, "mask":    0x10000, "min": 0, "max":   1},  #CLKOUT1_EN,
             "CLKOUT1_DIV": { "addr":  1, "loc":  8, "mask":     0xFF00, "min": 0, "max": 255},  #CLKOUT1_DIV,
             "CLKOUT1_DLY": { "addr":  1, "loc":  4, "mask":       0xF0, "min": 0, "max":  15},  #CLKOUT1_DLY,

             "CLKOUT2_MUX": { "addr":  2, "loc": 17, "mask":    0x60000, "min": 0, "max":   3},  #CLKOUT2_MUX,
              "CLKOUT2_EN": { "addr":  2, "loc": 16, "mask":    0x10000, "min": 0, "max":   1},  #CLKOUT2_EN,
             "CLKOUT2_DIV": { "addr":  2, "loc":  8, "mask":     0xFF00, "min": 0, "max": 255},  #CLKOUT2_DIV,
             "CLKOUT2_DLY": { "addr":  2, "loc":  4, "mask":       0xF0, "min": 0, "max":  15},  #CLKOUT2_DLY,

             "CLKOUT3_MUX": { "addr":  3, "loc": 17, "mask":    0x60000, "min": 0, "max":   3},  #CLKOUT3_MUX,
              "CLKOUT3_EN": { "addr":  3, "loc": 16, "mask":    0x10000, "min": 0, "max":   1},  #CLKOUT3_EN,
             "CLKOUT3_DIV": { "addr":  3, "loc":  8, "mask":     0xFF00, "min": 0, "max": 255},  #CLKOUT3_DIV,
             "CLKOUT3_DLY": { "addr":  3, "loc":  4, "mask":       0xF0, "min": 0, "max":  15},  #CLKOUT3_DLY,

             "CLKOUT4_MUX": { "addr":  4, "loc": 17, "mask":    0x60000, "min": 0, "max":   3},  #CLKOUT4_MUX,
              "CLKOUT4_EN": { "addr":  4, "loc": 16, "mask":    0x10000, "min": 0, "max":   1}, #CLKOUT4_EN,
             "CLKOUT4_DIV": { "addr":  4, "loc":  8, "mask":     0xFF00, "min": 0, "max": 255},  #CLKOUT4_DIV,
             "CLKOUT4_DLY": { "addr":  4, "loc":  4, "mask":       0xF0, "min": 0, "max":  15},  #CLKOUT4_DLY,

             "CLKOUT5_MUX": { "addr":  5, "loc": 17, "mask":    0x60000, "min": 0, "max":   3},  #CLKOUT5_MUX,
              "CLKOUT5_EN": { "addr":  5, "loc": 16, "mask":    0x10000, "min": 0, "max":   1},  #CLKOUT5_EN,
             "CLKOUT5_DIV": { "addr":  5, "loc":  8, "mask":     0xFF00, "min": 0, "max": 255},  #CLKOUT5_DIV,
             "CLKOUT5_DLY": { "addr":  5, "loc":  4, "mask":       0xF0, "min": 0, "max":  15},  #CLKOUT5_DLY,

             "CLKOUT6_MUX": { "addr":  6, "loc": 17, "mask":    0x60000, "min": 0, "max":   3},  #CLKOUT6_MUX,
              "CLKOUT6_EN": { "addr":  6, "loc": 16, "mask":    0x10000, "min": 0, "max":   1},  #CLKOUT6_EN,
             "CLKOUT6_DIV": { "addr":  6, "loc":  8, "mask":     0xFF00, "min": 0, "max": 255},  #CLKOUT6_DIV,
             "CLKOUT6_DLY": { "addr":  6, "loc":  4, "mask":       0xF0, "min": 0, "max":  15}, #CLKOUT6_DLY,

             "CLKOUT7_MUX": { "addr":  7, "loc": 17, "mask":    0x60000, "min": 0, "max":   3},  #CLKOUT7_MUX,
              "CLKOUT7_EN": { "addr":  7, "loc": 16, "mask":    0x10000, "min": 0, "max":   1},  #CLKOUT7_EN,
             "CLKOUT7_DIV": { "addr":  7, "loc":  8, "mask":     0xFF00, "min": 0, "max": 255}, #CLKOUT7_DIV,
             "CLKOUT7_DLY": { "addr":  7, "loc":  4, "mask":       0xF0, "min": 0, "max":  15},  #CLKOUT7_DLY,

                  "VBOOST": { "addr":  9, "loc": 16, "mask":    0x10000, "min": 0, "max":   1},  #VBOOST,
            "CLKIN_SELECT": { "addr": 14, "loc": 29, "mask": 0x20000000, "min": 0, "max":   1},  #CLKIN_SELECT,
        "EN_CLKOUT_GLOBAL": { "addr": 14, "loc": 27, "mask":  0x8000000, "min": 0, "max":   1},  #EN_CLKOUT_GLOBAL,
               "POWERDOWN": { "addr": 14, "loc": 26, "mask":  0x4000000, "min": 0, "max":   1}  #POWERDOWN,
}

    ADDRESS_INFO = []
    GPIO_PINS = []

    def __init__(self, path=None, mode=None, name="LMK01020"):
        self.__dict__ = {}
        self._name = name

        if path and mode:
            self.ADDRESS_INFO.append({'path': path, 'mode': mode})
            _logger.debug("Instantiated LMK01020 device with path: " + str(path) + " and mode: " + str(mode))
        self.from_dict_plat()

        self.LMK01020CurParams = [0] * 15

        self.LMK01020CurParams[9] = 0x22A00
        self.LMK01020CurParams[14] = 0x40000000

    def from_dict_plat(self):
        for key, value in self.REGISTERS_INFO.items():
            value = Command(value, str(key), self)
            self.__dict__[key] = value

    def register_device(self, channel, address):
        self.ADDRESS_INFO.append({'path': channel, 'mode': address})
        _logger.debug("Added LMK01020 device with path: " + str(channel) + " and mode: " + str(address))

    def device_summary(self):
        report = ""
        for addr in self.ADDRESS_INFO:
            report += ('{DeviceName: <10} :: Path:{Path: >3}, Mode:{Mode: >4}(0x{Mode:02X})\n'.format(DeviceName=self._name, Path=addr['path'], Mode=addr['mode']))
        return report

    def __repr__(self):
        return self._name

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]


    def write_param(self, devNum, paramName, value):
        if not (paramName in self.REGISTERS_INFO):
            _logger.error(str(paramName) + " is an invalid parameter name")
            return -1

        if paramName in self.REGISTERS_INFO:
            paramInfo = self.REGISTERS_INFO[paramName]
        elif paramName in self.GPIO_PINS[devNum]:
            self.gpio_set(devNum=devNum, name=paramName, value=value)
            return 0
        else:
            _logger.error("{paramName} is an unknown parameter or pin name.".format(paramName=paramName))
            return -1

        if not self.ADDRESS_INFO:
            _logger.error("No Devices registered. Aborting...")
            return -1

        spi_path = self.ADDRESS_INFO[devNum]["path"]
        spi_mode = self.ADDRESS_INFO[devNum]["mode"]

        if (1 == paramInfo["min"]) and (1 == paramInfo["max"]):
            _logger.error(str(paramName) + " is a read-only parameter")
            return -1

        if (value < paramInfo["min"]) or (value > paramInfo["max"]):
            _logger.error("{value} is an invalid value for {paramName}. " +
                          "Must be between {min} and {max}".format(value=value,
                                                                   paramName=paramName,
                                                                   min=paramInfo["min"],
                                                                   max=paramInfo["max"]))
            return -1

        # Positions to appropriate bits
        value <<= paramInfo["loc"]
        # Restrain to concerned bits
        value &= paramInfo["mask"]

        value = self.register_exceptions(paramInfo, value)

        self.LMK01020CurParams[paramInfo['addr']] = (~paramInfo['mask'] & self.LMK01020CurParams[paramInfo['addr']]) | value

        with SPI(spi_path, spi_mode, 1000000) as spi:
            writeBuf = self.LMK01020CurParams[paramInfo['addr']].to_bytes(4, 'big')
            _logger.debug("About to write raw data: " + str(writeBuf))
            spi.transfer(writeBuf)

        return 0


    # Here are all the formatting exceptions for registers.
    def register_exceptions(self, paramInfo, value):
        return value


    def selftest(self, devNum):
        # lmk01020 is write-only, skip self-test
        return 1


    def readout_all_registers(self, devNum):
        _logger.info("==== Device report ====")
        _logger.warning("lmk01020 is write-only, skipping...")
        return 0

    def gpio_set(self, devNum, name, value):
        if not self.GPIO_PINS:
            _logger.warning("No gpio pins defined. Aborting...")
            return -1

        if name in self.GPIO_PINS[devNum]:
            pin = self.GPIO_PINS[devNum][name]
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

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='LMK01020 utility program.')
    parser.add_argument('channel', help='I2C channel')
    parser.add_argument('address', help='I2C address')
    parser.add_argument('param', help='Parameter name')
    parser.add_argument('-w', default=False, action='store_true', help='Write flag')

    args = parser.parse_args()
    print((args))
