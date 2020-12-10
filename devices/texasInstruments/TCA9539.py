import time
import smbus
import logging
from periphery import GPIO

_logger = logging.getLogger(__name__)

class TCA9539:

    DEVICE_NAME = "TCA9539"

    #All register info concerning all LMK parameters
    REGISTERS_INFO = {
        #  if min=max=0, read-only, min=max=1 Self-clearing)
        "INPUTPORT0":             { "addr": 0, "loc": 0, "mask": 0xFF, "regs": 1, "min": 0, "max": 0},
        "INPUTPORT1":             { "addr": 1, "loc": 0, "mask": 0xFF, "regs": 1, "min": 0, "max": 0},
        "OUTPUTPORT0":            { "addr": 2, "loc": 0, "mask": 0xFF, "regs": 1, "min": 0, "max": 0xFF},
        "OUTPUTPORT1":            { "addr": 3, "loc": 0, "mask": 0xFF, "regs": 1, "min": 0, "max": 0xFF},
        "POLARITYINVERSIONPORT0": { "addr": 4, "loc": 0, "mask": 0xFF, "regs": 1, "min": 0, "max": 0xFF},
        "POLARITYINVERSIONPORT1": { "addr": 5, "loc": 0, "mask": 0xFF, "regs": 1, "min": 0, "max": 0xFF},
        "CONFIGURATIONPORT0":     { "addr": 6, "loc": 0, "mask": 0xFF, "regs": 1, "min": 0, "max": 0xFF},
        "CONFIGURATIONPORT1":     { "addr": 7, "loc": 0, "mask": 0xFF, "regs": 1, "min": 0, "max": 0xFF},
}

    ADDRESS_INFO = []
    GPIO_PINS = []

    def __init__(self, i2c_ch=None, i2c_addr=None, name="LMK03318"):
        self._name = name
        self.__dict__ = {}
        if i2c_ch and i2c_addr:
            self.ADDRESS_INFO.append({'ch': i2c_ch, 'addr': i2c_addr})
        self.from_dict_plat()

    def from_dict_plat(self):
        for key, value in self.REGISTERS_INFO.items():
            value = Command(value, str(key), self)
            self.__dict__[key] = value

    def register_device(self, channel, address):
        self.ADDRESS_INFO.append({'ch': channel, 'addr': address})

    def __repr__(self):
        return self._name

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]

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

        val = int.from_bytes(retVal, byteorder='big', signed=False)

        # Restrain to concerned bits
        val &= paramInfo['mask']
        # Positions to appropriate bits
        val >>= paramInfo['loc']

        val = self.register_exceptions(paramInfo, val)

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

        # Positions to appropriate bits
        value <<= paramInfo["loc"]
        # Restrain to concerned bits
        value &= paramInfo["mask"]

        value = self.register_exceptions(paramInfo, value)
        try:
            bus = smbus.SMBus(i2c_ch)
            currVal = bus.read_i2c_block_data(i2c_addr, paramInfo["addr"], paramInfo["regs"])
            writeBuf = (value).to_bytes(paramInfo["regs"], 'big')
            for i in range(paramInfo["regs"]-1):
                writeBuf[i] |= (currVal[i] & (~paramInfo["mask"] >> 8 * i))

            bus.write_i2c_block_data(i2c_addr, paramInfo["addr"], writeBuf)
            bus.close()
        except FileNotFoundError as e:
            _logger.error(e)
            _logger.error("Could not find i2c bus at channel: " + str(i2c_ch) + ", address: " + str(
                i2c_addr) + ". Check your connection....")
            return -1

        return 0

    # Here are all the formatting exceptions for registers.
    def register_exceptions(self, paramInfo, value):
        return value

    def selftest(self, devNum):
        i2c_addr = self.ADDRESS_INFO[devNum]['addr']
        i2c_ch = self.ADDRESS_INFO[devNum]['ch']
        val = self.read_param(i2c_ch, i2c_addr, "VNDRID")

        if (val != 0x100B):
            _logger.error("Self-test for device on channel: " + str(i2c_ch) + " at address: " + str(
                i2c_addr) + " failed")
            return -1

        return 0

    def readout_all_registers(self, devNum):
        i2c_addr = self.ADDRESS_INFO[devNum]['addr']
        i2c_ch = self.ADDRESS_INFO[devNum]['ch']
        _logger.info("==== Device report ====")
        _logger.info("Device Name: " + str(self.DEVICE_NAME))
        _logger.info("I2C channel: " + str(i2c_ch) + " I2C address: " + str(i2c_addr))
        for key in self.REGISTERS_INFO:
            val = self.read_param(i2c_ch, i2c_addr, key)
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

