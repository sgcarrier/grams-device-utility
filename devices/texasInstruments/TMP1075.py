import time
import smbus
import logging
from periphery import GPIO

_logger = logging.getLogger(__name__)

class TMP1075:
    """
        Class for the TMP1075, a 12-Bit I2C and SMBus I/O Temperature sensor
        The TMP175 is a write-read device that communicates via I2C.

        User Notes: -
    """

    DEVICE_NAME = "TMP1075"

    #All register info concerning all LMK parameters
    REGISTERS_INFO = {
        #  if min=max=0, read-only, min=max=1 Self-clearing)
        "T":   { "addr":  0, "loc":  4, "mask": 0xFFF0, "regs": 1, "min": 0, "max":     0},
        "SD":  { "addr":  1, "loc":  8, "mask":  0x100, "regs": 1, "min": 0, "max":     1},
        "TM":  { "addr":  1, "loc":  9, "mask":  0x200, "regs": 1, "min": 0, "max":     1},
        "POL": { "addr":  1, "loc": 10, "mask":  0x400, "regs": 1, "min": 0, "max":     1},
        "F":   { "addr":  1, "loc": 11, "mask": 0x1800, "regs": 1, "min": 0, "max":     3},
        "R":   { "addr":  1, "loc": 13, "mask": 0x6000, "regs": 1, "min": 0, "max":     3},
        "OS":  { "addr":  1, "loc": 15, "mask": 0x8000, "regs": 1, "min": 0, "max":     1},
        "L":   { "addr":  3, "loc":  4, "mask": 0xFFF0, "regs": 1, "min": 0, "max": 0xFFF},
        "H":   { "addr":  3, "loc":  4, "mask": 0xFFF0, "regs": 1, "min": 0, "max": 0xFFF},
        "DID": { "addr": 15, "loc":  0, "mask": 0xFFFF, "regs": 1, "min": 0, "max":     0},
}

    ADDRESS_INFO = []
    GPIO_PINS = []

    def __init__(self, i2c_ch=None, i2c_addr=None, name="TMP1075"):
        self.__dict__ = {}
        self._name = name
        if i2c_ch and i2c_addr:
            self.ADDRESS_INFO.append({'ch': i2c_ch, 'addr': i2c_addr})
            _logger.debug("Instantiated TMP1075 device with ch: " + str(i2c_ch) + " and addr: " + str(i2c_addr))

        ''' Populate add all the registers as attributes '''
        for key, value in self.REGISTERS_INFO.items():
            value = Command(value, str(key), self)
            self.__dict__[key] = value


    def register_device(self, channel, address):
        self.ADDRESS_INFO.append({'ch': channel, 'addr': address})
        _logger.debug("Added TMP1075 device with ch: " + str(channel) + " and addr: " + str(address))

    def device_summary(self):
        report = ""
        for addr in self.ADDRESS_INFO:
            report += ('{DeviceName: <10} :: Channel:{Channel: >3}, Address:{Address: >4}(0x{Address:02X})\n'.format(DeviceName=self._name, Channel=addr['ch'], Address=addr['addr']))
        return report



    # Read temperature registers and calculate Celsius
    def read_param(self, devNum, paramName):
        if not (paramName in self.REGISTERS_INFO):
            _logger.error( str(paramName) + " is an invalid parameter name")
            return -1

        if paramName in self.REGISTERS_INFO:
            paramInfo = self.REGISTERS_INFO[paramName]
        else:
            _logger.error("{paramName} is an unknown parameter.".format(paramName=paramName))
            return -1

        if not self.ADDRESS_INFO:
            _logger.error("No Devices registered. Aborting...")
            return -1

        i2c_addr = self.ADDRESS_INFO[devNum]['addr']
        i2c_ch = self.ADDRESS_INFO[devNum]['ch']

        try:
            bus = smbus.SMBus(i2c_ch)
            retVal = bus.read_i2c_block_data(i2c_addr, paramInfo["addr"], paramInfo["regs"])
            bus.close()
        except FileNotFoundError as e:
            _logger.error(e)
            _logger.error("Could not find i2c bus at channel: " + str(i2c_ch) + ", address: " + str(
                i2c_addr) + ". Check your connection....")
            return -1
        except Exception as e:
            _logger.error("Could not set message to device. Check connection...")
            _logger.error(e)
            return -1

        val = int.from_bytes(retVal, byteorder='big', signed=False)

        ''' Data formating from the register '''
        val &= paramInfo['mask']
        val >>= paramInfo['loc']
        val = self.register_exceptions(paramInfo, val)

        time.sleep(0.01)
        return val

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

        i2c_addr = self.ADDRESS_INFO[devNum]['addr']
        i2c_ch = self.ADDRESS_INFO[devNum]['ch']

        if (0 == paramInfo["min"]) and (0 == paramInfo["max"]):
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

        try:
            bus = smbus.SMBus(i2c_ch)

            ''' Retrieve value in register '''
            currVal = bus.read_i2c_block_data(i2c_addr, paramInfo["addr"], paramInfo["regs"])
            _logger.debug("In register " + str(paramName) + " = " + str([hex(no) for no in currVal]))
            currVal = int.from_bytes(currVal, byteorder='big')
            ''' Clear all bits concerned with our parameter and keep the others we dont want to affect
                Note this might cause problems if your python is not 64-bits and registers are >32bits '''
            currVal_cleared = currVal & (~paramInfo["mask"])
            ''' Write new value for the parameter '''
            newVal = value + currVal_cleared
            ''' Package as a byte-list '''
            writeBuf = self.int_to_short_list(newVal, fixed_length=paramInfo["regs"])

            _logger.debug("To register " + str(paramName) + " = " + str([hex(no) for no in writeBuf]))
            bus.write_i2c_block_data(i2c_addr, paramInfo["addr"], writeBuf)
            bus.close()
        except FileNotFoundError as e:
            _logger.error(e)
            _logger.error("Could not find i2c bus at channel: " + str(i2c_ch) + ", address: " + str(
                i2c_addr) + ". Check your connection....")
            return -1
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
            while (data != 0):
                retList.append(data & 0xFF)
                data = data >> 8
        if invert:
            return retList
        else:
            return retList[::-1]

    ''' Here are all the formatting exceptions for registers. '''
    def register_exceptions(self, paramInfo, value):
        return value

    def selftest(self, devNum):
        i2c_addr = self.ADDRESS_INFO[devNum]['addr']
        i2c_ch = self.ADDRESS_INFO[devNum]['ch']
        val = self.read_param(devNum, "DID")

        if (val != 0x7500):
            _logger.error("Self-test for device on channel: " + str(i2c_ch) + " at address: " + str(
                i2c_addr) + " failed")
            _logger.error("Expecting: " + str(0x7500) + ", Received: " + str(val))
            return -1

        return 0

    def readout_all_registers(self, devNum):
        i2c_addr = self.ADDRESS_INFO[devNum]['addr']
        i2c_ch = self.ADDRESS_INFO[devNum]['ch']
        _logger.info("==== Device report ====")
        _logger.info("Device Name: " + str(self.DEVICE_NAME))
        _logger.info("I2C channel: " + str(i2c_ch) + " I2C address: " + str(i2c_addr))
        for key in self.REGISTERS_INFO:
            val = self.read_param(devNum, key)
            _logger.info('Param Name: {ParamName: <20}, Param Value: {Value: <16}'.format(ParamName=key, Value=val))

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
        if len(args) == 2:
            self._acc.write_param(args[0], self._name, args[1])
        elif len(args) == 1:
            return self._acc.read_param(args[0], self._name)
        else:
            _logger.warning("Incorrect number of arguments. Ignoring")

        time.sleep(0.01)

    def __repr__(self):
        return self._name

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]

