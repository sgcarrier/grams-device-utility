import time
import logging
from periphery import SPI, GPIO

_logger = logging.getLogger(__name__)

class LMK01020:
    """
        Class for the LMK01020, a High Performance Clock Buffer, Divider, and Distributor
        The LMK01020 is a write-only device that communicates via SPI (uwire)

        User Notes:

        - The default used clock is CLK1, change it with CLKIN_SELECT

        - The Clock division is actually 2x what you put in CLKoutX_DIV

        - Toggle SYNC pin at least once (low-High)

        - Don't forget the GOE pin for output

    """


    DEVICE_NAME = "LMK01020"

    ''' All register info concerning all LMK01020 parameters '''
    REGISTERS_INFO = {
        #  if min=max=0, read-only, min=max=1 Self-clearing)
                   "RESET": { "addr":  0, "loc": 31, "mask": 0x80000000, "min": 0, "max":   1, "info": "Test"},  # RESET,
             "CLKOUT0_MUX": { "addr":  0, "loc": 17, "mask":    0x60000, "min": 0, "max":   3, "info": "Test"},  #CLKOUT0_MUX,
              "CLKOUT0_EN": { "addr":  0, "loc": 16, "mask":    0x10000, "min": 0, "max":   1, "info": "Test"},  #CLKOUT0_EN,
             "CLKOUT0_DIV": { "addr":  0, "loc":  8, "mask":     0xFF00, "min": 0, "max": 255, "info": "Test"},  #CLKOUT0_DIV,
             "CLKOUT0_DLY": { "addr":  0, "loc":  4, "mask":       0xF0, "min": 0, "max":  15, "info": "Test"},  #CLKOUT0_DLY,

             "CLKOUT1_MUX": { "addr":  1, "loc": 17, "mask":    0x60000, "min": 0, "max":   3, "info": "Test"},  #CLKOUT1_MUX,
              "CLKOUT1_EN": { "addr":  1, "loc": 16, "mask":    0x10000, "min": 0, "max":   1, "info": "Test"},  #CLKOUT1_EN,
             "CLKOUT1_DIV": { "addr":  1, "loc":  8, "mask":     0xFF00, "min": 0, "max": 255, "info": "Test"},  #CLKOUT1_DIV,
             "CLKOUT1_DLY": { "addr":  1, "loc":  4, "mask":       0xF0, "min": 0, "max":  15, "info": "Test"},  #CLKOUT1_DLY,

             "CLKOUT2_MUX": { "addr":  2, "loc": 17, "mask":    0x60000, "min": 0, "max":   3, "info": "Test"},  #CLKOUT2_MUX,
              "CLKOUT2_EN": { "addr":  2, "loc": 16, "mask":    0x10000, "min": 0, "max":   1, "info": "Test"},  #CLKOUT2_EN,
             "CLKOUT2_DIV": { "addr":  2, "loc":  8, "mask":     0xFF00, "min": 0, "max": 255, "info": "Test"},  #CLKOUT2_DIV,
             "CLKOUT2_DLY": { "addr":  2, "loc":  4, "mask":       0xF0, "min": 0, "max":  15, "info": "Test"},  #CLKOUT2_DLY,

             "CLKOUT3_MUX": { "addr":  3, "loc": 17, "mask":    0x60000, "min": 0, "max":   3, "info": "Test"},  #CLKOUT3_MUX,
              "CLKOUT3_EN": { "addr":  3, "loc": 16, "mask":    0x10000, "min": 0, "max":   1, "info": "Test"},  #CLKOUT3_EN,
             "CLKOUT3_DIV": { "addr":  3, "loc":  8, "mask":     0xFF00, "min": 0, "max": 255, "info": "Test"},  #CLKOUT3_DIV,
             "CLKOUT3_DLY": { "addr":  3, "loc":  4, "mask":       0xF0, "min": 0, "max":  15, "info": "Test"},  #CLKOUT3_DLY,

             "CLKOUT4_MUX": { "addr":  4, "loc": 17, "mask":    0x60000, "min": 0, "max":   3, "info": "Test"},  #CLKOUT4_MUX,
              "CLKOUT4_EN": { "addr":  4, "loc": 16, "mask":    0x10000, "min": 0, "max":   1, "info": "Test"}, #CLKOUT4_EN,
             "CLKOUT4_DIV": { "addr":  4, "loc":  8, "mask":     0xFF00, "min": 0, "max": 255, "info": "Test"},  #CLKOUT4_DIV,
             "CLKOUT4_DLY": { "addr":  4, "loc":  4, "mask":       0xF0, "min": 0, "max":  15, "info": "Test"},  #CLKOUT4_DLY,

             "CLKOUT5_MUX": { "addr":  5, "loc": 17, "mask":    0x60000, "min": 0, "max":   3, "info": "Test"},  #CLKOUT5_MUX,
              "CLKOUT5_EN": { "addr":  5, "loc": 16, "mask":    0x10000, "min": 0, "max":   1, "info": "Test"},  #CLKOUT5_EN,
             "CLKOUT5_DIV": { "addr":  5, "loc":  8, "mask":     0xFF00, "min": 0, "max": 255, "info": "Test"},  #CLKOUT5_DIV,
             "CLKOUT5_DLY": { "addr":  5, "loc":  4, "mask":       0xF0, "min": 0, "max":  15, "info": "Test"},  #CLKOUT5_DLY,

             "CLKOUT6_MUX": { "addr":  6, "loc": 17, "mask":    0x60000, "min": 0, "max":   3, "info": "Test"},  #CLKOUT6_MUX,
              "CLKOUT6_EN": { "addr":  6, "loc": 16, "mask":    0x10000, "min": 0, "max":   1, "info": "Test"},  #CLKOUT6_EN,
             "CLKOUT6_DIV": { "addr":  6, "loc":  8, "mask":     0xFF00, "min": 0, "max": 255, "info": "Test"},  #CLKOUT6_DIV,
             "CLKOUT6_DLY": { "addr":  6, "loc":  4, "mask":       0xF0, "min": 0, "max":  15, "info": "Test"}, #CLKOUT6_DLY,

             "CLKOUT7_MUX": { "addr":  7, "loc": 17, "mask":    0x60000, "min": 0, "max":   3, "info": "Test"},  #CLKOUT7_MUX,
              "CLKOUT7_EN": { "addr":  7, "loc": 16, "mask":    0x10000, "min": 0, "max":   1, "info": "Test"},  #CLKOUT7_EN,
             "CLKOUT7_DIV": { "addr":  7, "loc":  8, "mask":     0xFF00, "min": 0, "max": 255, "info": "Test"}, #CLKOUT7_DIV,
             "CLKOUT7_DLY": { "addr":  7, "loc":  4, "mask":       0xF0, "min": 0, "max":  15, "info": "Test"},  #CLKOUT7_DLY,

                  "VBOOST": { "addr":  9, "loc": 16, "mask":    0x10000, "min": 0, "max":   1, "info": "Test"},  #VBOOST,
            "CLKIN_SELECT": { "addr": 14, "loc": 29, "mask": 0x20000000, "min": 0, "max":   1, "info": "Test"},  #CLKIN_SELECT,
        "EN_CLKOUT_GLOBAL": { "addr": 14, "loc": 27, "mask":  0x8000000, "min": 0, "max":   1, "info": "Test"},  #EN_CLKOUT_GLOBAL,
               "POWERDOWN": { "addr": 14, "loc": 26, "mask":  0x4000000, "min": 0, "max":   1, "info": "Test"}  #POWERDOWN,
}
    ADDRESS_INFO = []
    GPIO_PINS = []





    def __init__(self, path=None, mode=None, name="LMK01020", accessor=None):
        self.__dict__ = {}
        self._name = name

        if path and mode:
            self.ADDRESS_INFO.append({'path': path, 'mode': mode})
            _logger.debug("Instantiated LMK01020 device with path: " + str(path) + " and mode: " + str(mode))

        ''' Populate add all the registers as attributes '''
        for key, value in self.REGISTERS_INFO.items():
            value = Command(value, str(key), self)
            self.__dict__[key] = value



        ''' Since the LMK01020 is write-only, we keep a local copy of registers '''
        self.LMK01020CurParams = [0] * 15
        self.LMK01020CurParams[9] = 0x22A00
        self.LMK01020CurParams[14] = 0x40000000

    def register_device(self, channel, address):
        self.ADDRESS_INFO.append({'path': channel, 'mode': address})
        _logger.debug("Added LMK01020 device with path: " + str(channel) + " and mode: " + str(address))

    def device_summary(self):
        report = ""
        for addr in self.ADDRESS_INFO:
            report += ('{DeviceName: <10} :: Path:{Path: >3}, Mode:{Mode: >4}(0x{Mode:02X})\n'.format(DeviceName=self._name, Path=addr['path'], Mode=addr['mode']))
        return report

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

        ''' Data formating to put into the register '''
        value <<= paramInfo["loc"]
        value &= paramInfo["mask"]

        value = self.register_exceptions(paramInfo, value)

        self.LMK01020CurParams[paramInfo['addr']] = (~paramInfo['mask'] & self.LMK01020CurParams[paramInfo['addr']]) | value
        try:
            bus = SPI(spi_path, spi_mode, 1000000)
            to_send =self.LMK01020CurParams[paramInfo['addr']] + paramInfo['addr']
            writeBuf = self.int_to_short_list(to_send, fixed_length=4)
            _logger.debug("Writing raw data: " + str([hex(no) for no in writeBuf]))
            bus.transfer(writeBuf)
            bus.close()
        except Exception as e:
            _logger.error("Could not set message to device. Check connection...")
            _logger.error(e)
            return -1

        time.sleep(0.01)
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

    def __repr__(self):
        return self._name

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]


class Command:
    """
    This class allows us to use all registers as attributes. Calling the registers with different number of arguments calls
    a read or write operation, depending on what is available.

    For example:
    > d = Device()
    > d.register_name(0)  # read operation of the device number 0
    > d.register_name(0, 1) # writing 1 to the device 0
    """

    def __init__(self, d, name="", acc=None):
        self.__dict__ = {}
        self._name = name
        self._acc = acc
        self.__doc__ = d["info"]

    def __call__(self, *args):
        if len(args) == 2:
            self._acc.write_param(args[0], self._name, args[1])
        else:
            _logger.warning("Incorrect number of arguments. Ignoring")

        time.sleep(0.01)


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
