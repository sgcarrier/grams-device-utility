import time
import logging
from periphery import SPI, GPIO

_logger = logging.getLogger(__name__)

class AD5668:
    """
        Class for the AD5668, a 16-bit DAC with 8 outputs.
        The AD5568 is a write-only device and communicates via SPI

        User Notes:
        - Input BIG endian data into the SPI line
        - The AD5668 reads data on the FALLING edge of the clocks (SPI MODE 1)
        - All transactions MUST have 32 clock cycles (4 bytes) or else it will be ignored.
        - For quick setup: 'INTERNAL_REF_SETUP = 1' followed by 'WRITE_TO_AND_UPDATE_DAC = Value' you want

    """

    DEVICE_NAME = "AD5668"

    #All register info concerning all AD5668 parameters
    REGISTERS_INFO = {
        #  if min=max=0, read-only, min=max=1 Self-clearing)
    "WRITE_TO_INPUT_REGISTER"           : { "addr":  0, "loc": 4, "mask": 0xFFFFFFFF, "min": 0, "max": 0xFFFF},  # WRITE_TO_INPUT_REGISTER,
    "UPDATE_DAC_REGISTER"               : { "addr":  1, "loc": 4, "mask": 0xFFFFFFFF, "min": 0, "max": 0xFFFF},  #UPDATE_DAC_REGISTER,
    "WRITE_TO_INPUT_REGISTER_UPDATE_ALL": { "addr":  2, "loc": 4, "mask": 0xFFFFFFFF, "min": 0, "max": 0xFFFF},  #WRITE_TO_INPUT_REGISTER_UPDATE_ALL,
    "WRITE_TO_AND_UPDATE_DAC"           : { "addr":  3, "loc": 4, "mask": 0xFFFFFFFF, "min": 0, "max": 0xFFFF},  #WRITE_TO_AND_UPDATE_DAC,
    "DAC_ON_OFF"                        : { "addr":  4, "loc": 0, "mask": 0xFFFFFFFF, "min": 0, "max": 0xFFFF},  #DAC_ON_OFF,
    "LOAD_CLEAR_CODE_REGISTER"          : { "addr":  5, "loc": 4, "mask": 0xFFFFFFFF, "min": 0, "max": 0xFFFF},  #LOAD_CLEAR_CODE_REGISTER,
    "LOAD_LDAC_REGISTER"                : { "addr":  6, "loc": 4, "mask": 0xFFFFFFFF, "min": 0, "max": 0xFFFF},  #LOAD_LDAC_REGISTER,
    "RESET"                             : { "addr":  7, "loc": 0, "mask": 0xFFFFFFFF, "min": 0, "max": 0xFFFF},  #RESET,
    "INTERNAL_REF_SETUP"                : { "addr":  8, "loc": 0, "mask": 0xFFFFFFFF, "min": 0, "max": 0xFFFF}   #INTERNAL_REF_SETUP
    }

    ADDRESS_INFO = []
    GPIO_PINS = {}

    def __init__(self, path=None, mode=None, name="AD5668"):
        self.__dict__ = {}
        self._name = name

        if path and mode:
            self.ADDRESS_INFO.append({'path': path, 'mode': mode})

        ''' Populate add all the registers as attributes '''
        for key, value in self.REGISTERS_INFO.items():
            value = Command(value, str(key), self)
            self.__dict__[key] = value

    def register_device(self, channel, address):
        self.ADDRESS_INFO.append({'path': channel, 'mode': address})

    def device_summary(self):
        report = ""
        for addr in self.ADDRESS_INFO:
            report += ('{DeviceName: <10} :: Path:{Path: >3}, Mode:{Mode: >4}(0x{Mode:02X})\n'.format(DeviceName=self._name, Path=addr['path'], Mode=addr['mode']))
        return report

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

        """Data formating to put into the register"""
        value <<= paramInfo["loc"]
        value &= paramInfo["mask"]

        value = self.register_exceptions(paramInfo, value)

        value |= (dacNum << 20)
        value |= (paramInfo['addr'] << 24)

        try:
            with SPI(spi_path, spi_mode, 1000000) as spi:
                writeBuf = self.int_to_short_list(value, 4)
                _logger.debug("About to write raw data: " + str(writeBuf))
                spi.transfer(writeBuf)
        except Exception as e:
            _logger.error("Could not set message to device. Check connection...")
            _logger.error(e)
            return -1

        return 0

    """
    Converts an integer to a list of byte-size shorts.
    Ex:    idx          0     1     2
        0x123456 --> [0x12, 0x34, 0x56] (invert=False) (BIG_ENDIAN)
        0x123456 --> [0x56, 0x34, 0x12] (invert=True)  (LITTLE ENDIAN)
    """
    def int_to_short_list(self, data, fixed_length=None, invert=False):
        retList = []
        if fixed_length:
            for i in range(fixed_length):
                retList.append(data & 0xFF)
                data = data >> 8
        else:
            while(data != 0):
                retList.append(data & 0xFF)
                data = data >> 8
        if invert:
            return retList
        else:
            return retList[::-1]

    # Here are all the formatting exceptions for registers.
    def register_exceptions(self, paramInfo, value):
        return value

    def selftest(self, devNum):
        # ad5668 is write-only, skip self-test
        return 1

    def readout_all_registers(self, devNum):
        _logger.info("==== Device report ====")
        _logger.warning("ad5668 is write-only, skipping...")
        return 0

    def __repr__(self):
        return self._name

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]

"""
This class allows us to use all registers as attributes. Calling the registers with different number of arguments calls
a read or write operation, depending on what is available
"""
class Command():
    def __init__(self, d, name="", acc=None):
        self.__dict__ = {}
        self._name = name
        self._acc = acc

    def __call__(self, *args):
        if len(args) == 3:
            self._acc.write_param(args[0], self._name, args[1], args[2])
        else:
            _logger.warning("Incorrect number of arguments. Ignoring")

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
