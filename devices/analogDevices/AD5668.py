import time
import logging
from periphery import SPI, GPIO

_logger = logging.getLogger(__name__)

class LMK01020:

    DEVICE_NAME = "AD5668"

    #All register info concerning all LMK parameters
    REGISTERS_INFO = {
        #  if min=max=0, read-only, min=max=1 Self-clearing)
    "WRITE_TO_INPUT_REGISTER"           : { "addr":  0, "loc": 0, "mask": 0xFFFFFFFF, "min": 0, "max": 0xFFFF},  # WRITE_TO_INPUT_REGISTER,
    "UPDATE_DAC_REGISTER"               : { "addr":  1, "loc": 0, "mask": 0xFFFFFFFF, "min": 0, "max": 0xFFFF},  #UPDATE_DAC_REGISTER,
    "WRITE_TO_INPUT_REGISTER_UPDATE_ALL": { "addr":  2, "loc": 0, "mask": 0xFFFFFFFF, "min": 0, "max": 0xFFFF},  #WRITE_TO_INPUT_REGISTER_UPDATE_ALL,
    "WRITE_TO_AND_UPDATE_DAC"           : { "addr":  3, "loc": 0, "mask": 0xFFFFFFFF, "min": 0, "max": 0xFFFF},  #WRITE_TO_AND_UPDATE_DAC,
    "DAC_ON_OFF"                        : { "addr":  4, "loc": 4, "mask": 0xFFFFFFFF, "min": 0, "max": 0xFFFF},  #DAC_ON_OFF,
    "LOAD_CLEAR_CODE_REGISTER"          : { "addr":  5, "loc": 0, "mask": 0xFFFFFFFF, "min": 0, "max": 0xFFFF},  #LOAD_CLEAR_CODE_REGISTER,
    "LOAD_LDAC_REGISTER"                : { "addr":  6, "loc": 0, "mask": 0xFFFFFFFF, "min": 0, "max": 0xFFFF},  #LOAD_LDAC_REGISTER,
    "RESET"                             : { "addr":  7, "loc": 4, "mask": 0xFFFFFFFF, "min": 0, "max": 0xFFFF},  #RESET,
    "INTERNAL_REF_SETUP"                : { "addr":  8, "loc": 4, "mask": 0xFFFFFFFF, "min": 0, "max": 0xFFFF}   #INTERNAL_REF_SETUP
    }

    ADDRESS_INFO = []
    GPIO_PINS = {}

    def __init__(self, path=None, mode=None, name="AD5668"):
        self._name = name
        self.__dict__ = {}

        if path and mode:
            self.ADDRESS_INFO.append({'path': path, 'mode': mode})
        self.from_dict_plat()

    def from_dict_plat(self):
        for key, value in self.REGISTERS_INFO.items():
            value = Command(value, str(key), self)
            self.__dict__[key] = value

    def register_device(self, channel, address):
        self.ADDRESS_INFO.append({'path': channel, 'mode': address})

    def __repr__(self):
        return self._name

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]

    def write_param(self, devNum, paramName, dacNum, value):
        if not (paramName in self.REGISTERS_INFO):
            _logger.error(str(paramName) + " is an invalid parameter name")
            return -1

        if paramName in self.REGISTERS_INFO:
            paramInfo = self.REGISTERS_INFO[paramName]
        else:
            _logger.error("{paramName} is an unknown parameter.".format(paramName=paramName))
            return -1

        if not self.ADDRESS_INFO:
            _logger.error("No Devices registered. Aborting...")
            return -1

        spi_path = self.ADDRESS_INFO[devNum]["path"]
        spi_mode = self.ADDRESS_INFO[devNum]["mode"]

        if (dacNum < 0) or (dacNum > 0xF):
            _logger.error("{value} is an invalid value for {paramName}. Must be between {min} and {max}".format(value=dacNum,
                                                                                                                paramName="DAC number",
                                                                                                                min=0,
                                                                                                                max=0xF))
            return -1

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

        value |= (dacNum << 20)
        value |= (paramInfo['addr'] << 24)


        with SPI(spi_path, spi_mode, 1000000) as spi:
            writeBuf = self.swap_32bits(value).to_bytes(4, 'big')
            spi.transfer(writeBuf)

        return 0


    # Here are all the formatting exceptions for registers.
    def register_exceptions(self, paramInfo, value):
        return value


    def selftest(self, devNum):
        # ad5668 is write-only, skip self-test
        return 0

    def swap_32bits(self, val):
        val = ((val << 8) & 0xFF00FF00) | ((val >> 8) & 0xFF00FF);
        return (val << 16) | (val >> 16);


    def readout_all_registers(self, devNum):
        _logger.info("==== Device report ====")
        _logger.warning("ad5668 is write-only, skipping...")
        return 0

class Command():
    def __init__(self, d, name="", acc=None):
        self.__dict__ = {}
        self._name = name
        self._acc = acc

    def __call__(self, *args):
        try:
            if len(args) == 3:
                self._acc.write_param(args[0], self._name, args[1], args[2])
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

    parser = argparse.ArgumentParser(description='AD5668 utility program.')
    parser.add_argument('path', help='SPI path')
    parser.add_argument('mode', help='SPI mode')
    parser.add_argument('param', help='Parameter name')
    parser.add_argument('dacNum', help='dac number')
    parser.add_argument('-w', default=False, action='store_true', help='Write flag')

    args = parser.parse_args()
    print((args))
