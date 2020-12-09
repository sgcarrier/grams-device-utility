import time
import smbus
import logging
from periphery import GPIO

_logger = logging.getLogger(__name__)

class LMK61E2:

    DEVICE_NAME = "LMK61E2"

    #All register info concerning all LMK parameters
    REGISTERS_INFO = {
    #  if min=max=0, read-only, min=max=1 Self-clearing)
                "VNDRID":  { "addr":   0, "loc":   0, "mask":   0xFFFF, "regs":   2, "min":   0, "max":       0}, # LMK61E2_VNDRID
                "PRODID":  { "addr":   2, "loc":   0, "mask":     0xFF, "regs":   1, "min":   0, "max":       0}, # LMK61E2_PRODID
                 "REVID":  { "addr":   3, "loc":   0, "mask":     0xFF, "regs":   1, "min":   0, "max":       0}, # LMK61E2_REVID
              "SLAVEADR":  { "addr":   8, "loc":   1, "mask":     0xFE, "regs":   1, "min":   0, "max":       0}, # LMK61E2_SLAVEADR
                 "EEREV":  { "addr":   9, "loc":   0, "mask":     0xFF, "regs":   1, "min":   0, "max":       0}, # LMK61E2_EEREV
               "PLL_PDN":  { "addr":  10, "loc":   6, "mask":     0x40, "regs":   1, "min":   0, "max":       1}, # LMK61E2_PLL_PDN
                 "ENCAL":  { "addr":  10, "loc":   1, "mask":      0x2, "regs":   1, "min":   1, "max":       1}, # LMK61E2_ENCAL
              "AUTOSTRT":  { "addr":  10, "loc":   0, "mask":      0x1, "regs":   1, "min":   0, "max":       1}, # LMK61E2_AUTOSTRT
            "XO_CAPCTRL":  { "addr":  16, "loc":   0, "mask":   0xFF03, "regs":   2, "min":   0, "max":    1023}, # LMK61E2_XO_CAPCTRL    # warning: bits are positioned in oddly in registers
           "DIFF_OUT_PD":  { "addr":  21, "loc":   7, "mask":     0x80, "regs":   1, "min":   0, "max":       1}, # LMK61E2_DIFF_OUT_PD
               "OUT_SEL":  { "addr":  21, "loc":   0, "mask":      0x3, "regs":   1, "min":   0, "max":       3}, # LMK61E2_OUT_SEL
               "OUT_DIV":  { "addr":  22, "loc":   0, "mask":    0x1FF, "regs":   2, "min":   5, "max":     511}, # LMK61E2_OUT_DIV
                  "NDIV":  { "addr":  25, "loc":   0, "mask":    0xFFF, "regs":   2, "min":   1, "max":    4095}, # LMK61E2_NDIV
               "PLL_NUM":  { "addr":  27, "loc":   0, "mask": 0x3FFFFF, "regs":   3, "min":   0, "max": 4194303}, # LMK61E2_PLL_NUM
               "PLL_DEN":  { "addr":  30, "loc":   0, "mask": 0x3FFFFF, "regs":   3, "min":   1, "max": 4194303}, # LMK61E2_PLL_DEN
          "PLL_DTHRMODE":  { "addr":  33, "loc":   2, "mask":      0xC, "regs":   1, "min":   0, "max":       3}, # LMK61E2_PLL_DTHRMODE    # Only certain values allowed
             "PLL_ORDER":  { "addr":  33, "loc":   0, "mask":      0x3, "regs":   1, "min":   0, "max":       3}, # LMK61E2_PLL_ORDER    # Only certain values allowed
                 "PLL_D":  { "addr":  34, "loc":   5, "mask":     0x20, "regs":   1, "min":   0, "max":       1}, # LMK61E2_PLL_D
                "PLL_CP":  { "addr":  34, "loc":   0, "mask":      0xF, "regs":   1, "min":   4, "max":       8}, # LMK61E2_PLL_CP   # Only certain values allowed
    "PLL_CP_PHASE_SHIFT":  { "addr":  35, "loc":   4, "mask":     0x70, "regs":   1, "min":   0, "max":       7}, # LMK61E2_PLL_CP_PHASE_SHIFT
         "PLL_ENABLE_C3":  { "addr":  35, "loc":   2, "mask":      0x4, "regs":   1, "min":   0, "max":       1}, # LMK61E2_PLL_ENABLE_C3
             "PLL_LF_R2":  { "addr":  36, "loc":   0, "mask":     0xFF, "regs":   1, "min":   1, "max":     255}, # LMK61E2_PLL_LF_R2
             "PLL_LF_C1":  { "addr":  37, "loc":   0, "mask":      0x7, "regs":   1, "min":   0, "max":       7}, # LMK61E2_PLL_LF_C1   # true value of C1 = 5 + 50*PLL_LF_C1
             "PLL_LF_R3":  { "addr":  38, "loc":   0, "mask":     0x7F, "regs":   1, "min":   0, "max":     127}, # LMK61E2_PLL_LF_R3
            "PLL_LF_C3 ":  { "addr":  39, "loc":   0, "mask":      0x7, "regs":   1, "min":   0, "max":       7}, # LMK61E2_PLL_LF_C3   # true value of C1 = 5 + 50*PLL_LF_C1
          "PLL_CLSDWAIT":  { "addr":  42, "loc":   2, "mask":      0xC, "regs":   1, "min":   0, "max":       3}, # LMK61E2_PLL_CLSDWAIT
           "PLL_VCOWAIT":  { "addr":  42, "loc":   0, "mask":      0x3, "regs":   1, "min":   0, "max":       3}, # LMK61E2_PLL_VCOWAIT
               "NVMSCRC":  { "addr":  47, "loc":   0, "mask":     0xFF, "regs":   1, "min":   0, "max":       0}, # LMK61E2_NVMSCRC
                "NVMCNT":  { "addr":  48, "loc":   0, "mask":     0xFF, "regs":   1, "min":   0, "max":       0}, # LMK61E2_NVMCNT
             "REGCOMMIT":  { "addr":  49, "loc":   6, "mask":     0x40, "regs":   1, "min":   1, "max":       1}, # LMK61E2_REGCOMMIT
             "NVMCRCERR":  { "addr":  49, "loc":   5, "mask":     0x20, "regs":   1, "min":   0, "max":       0}, # LMK61E2_NVMCRCERR
            "NVMAUTOCRC":  { "addr":  49, "loc":   4, "mask":     0x10, "regs":   1, "min":   0, "max":       1}, # LMK61E2_NVMAUTOCRC
             "NVMCOMMIT":  { "addr":  49, "loc":   3, "mask":      0x8, "regs":   1, "min":   1, "max":       1}, # LMK61E2_NVMCOMMIT
               "NVMBUSY":  { "addr":  49, "loc":   2, "mask":      0x4, "regs":   1, "min":   0, "max":       0}, # LMK61E2_NVMBUSY
              "NVMERASE":  { "addr":  49, "loc":   1, "mask":      0x2, "regs":   1, "min":   1, "max":       1}, # LMK61E2_NVMERASE
                  "PROG":  { "addr":  49, "loc":   0, "mask":      0x1, "regs":   1, "min":   1, "max":       1}, # LMK61E2_PROG
                "MEMADR":  { "addr":  51, "loc":   0, "mask":     0x7F, "regs":   1, "min":   0, "max":     127}, # LMK61E2_MEMADR
                "NVMDAT":  { "addr":  52, "loc":   0, "mask":     0xFF, "regs":   1, "min":   0, "max":       0}, # LMK61E2_NVMDAT
                "RAMDAT":  { "addr":  53, "loc":   0, "mask":     0xFF, "regs":   1, "min":   0, "max":     255}, # LMK61E2_RAMDAT
               "NVMUNLK":  { "addr":  56, "loc":   0, "mask":     0xFF, "regs":   1, "min":   0, "max":     255}, # LMK61E2_NVMUNLK    # Protection to prevent inadvertent programming on EEPROM, trend carefully
                   "LOL":  { "addr":  66, "loc":   1, "mask":      0x2, "regs":   1, "min":   0, "max":       0}, # LMK61E2_LOL
                   "CAL":  { "addr":  66, "loc":   0, "mask":      0x1, "regs":   1, "min":   0, "max":       0}, # LMK61E2_CAL
               "SWR2PLL":  { "addr":  72, "loc":   1, "mask":      0x2, "regs":   1, "min":   1, "max":       1}  # LMK61E2_SWR2PLL
}

    ADDRESS_INFO = []
    GPIO_PINS = {}

    def __init__(self, i2c_ch=None, i2c_addr=None, name="LMK61E2"):
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
            print("ERROR :: LMK61E2 :: " + str(paramName) + " is an invalid parameter name")
            return -1

        paramInfo = self.REGISTERS_INFO[paramName]

        i2c_addr = self.ADDRESS_INFO[devNum]['addr']
        i2c_ch = self.ADDRESS_INFO[devNum]['ch']

        try:
            bus = smbus.SMBus(i2c_ch)
            retVal = bus.read_i2c_block_data(i2c_addr, paramInfo["addr"], paramInfo["regs"])
            bus.close()
        except FileNotFoundError as e:
            _logger.error(e)
            _logger.error("Could not find i2c bus at channel: " + str(i2c_ch) + ", address: " + str(i2c_addr) + ".Check your connection....")
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
            print("ERROR :: LMK61E2 :: " + str(paramName) + " is an invalid parameter name")
            return -1

        paramInfo = self.REGISTERS_INFO[paramName]

        i2c_addr = self.ADDRESS_INFO[devNum]['addr']
        i2c_ch = self.ADDRESS_INFO[devNum]['ch']

        if (1 == paramInfo["min"]) and (1 == paramInfo["max"]):
            print("ERROR :: LMK61E2 :: " + str(paramName) + " is a read-only parameter")
            return -1

        if (value < paramInfo["min"]) or (value > paramInfo["max"]):
            print("ERROR :: LMK61E2 :: " + str(value) + " is an invalid value")
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
            _logger.error("Could not find i2c bus at channel: " + str(i2c_ch) + ", address: " + str(i2c_addr) + ".Check your connection....")
            return -1

        return 0


    # Here are all the formatting exceptions for registers.
    # Example: XO_CAPCTRL orders its bits in reverse register order compared to others
    def register_exceptions(self, paramInfo, value):
        if paramInfo['addr'] == 16:
            tmp = value & 0x30
            value <<= 2
            value &= paramInfo['mask']
            value += (tmp >> 8)
        return value


    def selftest(self, devNum):

        i2c_addr = self.ADDRESS_INFO[devNum]['addr']
        i2c_ch = self.ADDRESS_INFO[devNum]['ch']
        val = self.read_param(i2c_ch, i2c_addr, "VNDRID")

        if (val != 0x100B):
            print("ERROR :: LMK61E2 :: Self-test for device on channel: " + str(i2c_ch) + " at address: " + str(i2c_addr) + " failed")
            return -1

        return 0

    def readout_all_registers(self, devNum):
        i2c_addr = self.ADDRESS_INFO[devNum]['addr']
        i2c_ch = self.ADDRESS_INFO[devNum]['ch']

        print("==== Device report ====")
        print("Device Name: " + str(self.DEVICE_NAME))
        print("I2C channel: " + str(i2c_ch) + " I2C address: " + str(i2c_addr))
        for key in self.REGISTERS_INFO:
            val = self.read_param(i2c_ch, i2c_addr, key)
            print('Param Name: {ParamName: <20}, Param Value: {Value: <16}'.format(ParamName=key, Value=val))

    def gpio_set(self, name, value):
        if not self.GPIO_PINS:
            _logger.warn("No gpio pins defined. Aborting...")
            return -1

        pin = self.GPIO_PINS[name]
        g = GPIO(pin, "out")
        g.write(value)
        g.close()


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
                _logger.warn("Incorrect number of arguments. Ignoring")
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

    parser = argparse.ArgumentParser(description='LMK61E2 utility program.')
    parser.add_argument('channel', help='I2C channel')
    parser.add_argument('address', help='I2C address')
    parser.add_argument('param', help='Parameter name')
    parser.add_argument('-w', default=False, action='store_true', help='Write flag')
    parser.add_argument('-r', default=False, action='store_true', help='Read flag')
    parser.add_argument('-s', default=False, action='store_true', help='Selftest flag')

    args = parser.parse_args()
    print((args))
