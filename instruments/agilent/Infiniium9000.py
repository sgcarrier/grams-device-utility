import visa
import sys
import time
import csv
import logging

_logger = logging.getLogger(__name__)

class Infiniium9000:
    """
        Class for the Agilent Infiniium9000 13Ghz oscilloscope
    """
    DEVICE_NAME = "Infiniium9000"

    ''' All register info concerning all LMK61E2 parameters '''
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
             "PLL_LF_C3":  { "addr":  39, "loc":   0, "mask":      0x7, "regs":   1, "min":   0, "max":       7}, # LMK61E2_PLL_LF_C3   # true value of C1 = 5 + 50*PLL_LF_C1
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

    def __init__(self, visa_addr=None, name="Infiniium"):
        self.__dict__ = {}
        self._name = name
        if visa_addr
            self.ADDRESS_INFO.append({'addr': visa_addr})
            _logger.debug("Instantiated Infiniium instrument with addr: " + str(visa_addr))

        ''' Populate add all the registers as attributes '''
        for key, value in self.REGISTERS_INFO.items():
            value = Command(value, str(key), self)
            self.__dict__[key] = value

        self.resourceManager = visa.ResourceManager('@py')

    def __del__(self):
        self.resourceManager.close()

    def register_device(self, address):
        self.ADDRESS_INFO.append({'addr': address})
        _logger.debug("Added Infiniium instrument with addr: " + str(address))

    def device_summary(self):
        report = ""
        for addr in self.ADDRESS_INFO:
            report += ('{DeviceName: <10} :: Address:{Address: >30})\n'.format(DeviceName=self._name, Address=addr['addr']))
        return report

    def read_param(self, devNum, paramName):
        if not (paramName in self.REGISTERS_INFO):
            _logger.error(str(paramName) + " is an invalid parameter name")
            return -1

        paramInfo = self.REGISTERS_INFO[paramName]

        visa_addr = self.ADDRESS_INFO[devNum]['addr']

        try:
            self.resourceManager = visa.ResourceManager('@py')
            session = self.resourceManager.open_resource(visa_addr)
            # For Serial and TCP/IP socket connections enable the read Termination Character, or read's will timeout
            if session.resource_name.startswith('ASRL') or session.resource_name.endswith('SOCKET'):
                session.read_termination = '\n'
            session.write()
            retVal = session.read()
        except visa.Error as e:
            _logger.error(e)
            _logger.error("Couldn't connect to " + str(visa_addr) + " . Aborting...")
        except Exception as e:
            _logger.error("Could not set message to device. Check connection...")
            _logger.error(e)
            return -1


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
            _logger.error("{value} is an invalid value for {paramName}. Must be between {min} and {max}".format(value=value,
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
            _logger.error("Could not find i2c bus at channel: " + str(i2c_ch) + ", address: " + str(i2c_addr) + ".Check your connection....")
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
            while(data != 0):
                retList.append(data & 0xFF)
                data = data >> 8
        if invert:
            return retList
        else:
            return retList[::-1]

    """ Here are all the formatting exceptions for registers. """
    def register_exceptions(self, paramInfo, value):
        return value


    def selftest(self, devNum):
        i2c_addr = self.ADDRESS_INFO[devNum]['addr']
        i2c_ch = self.ADDRESS_INFO[devNum]['ch']
        val = self.read_param(devNum, "VNDRID")

        if (val != 0x100B):
            _logger.error("Self-test for device on channel: " + str(i2c_ch) + " at address: " + str(i2c_addr) + " failed")
            _logger.error("Expecting: " + str(0x100B) + ", Received: " + str(val))
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



if __name__ == "__main__":

    exit()


