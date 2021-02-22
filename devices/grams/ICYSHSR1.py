import time
import smbus
import logging
from periphery import GPIO
from ctypes import *

_logger = logging.getLogger(__name__)

class ICYSHSR1:

    DEVICE_NAME = "ICYSHSR1"
    DEVICE_TYPE = "C_LIB"

    M_OFS = 480 #Matrix register offset

    REGISTERS_INFO = {
        #  if min=max=0, read-only, min=max=1 Self-clearing)
        # regs: max number of the register offset+1
                                 "ASIC_ID": {"addr":         0, "loc":  0, "mask": 0xFFFFFFFF, "regs":   1, "min": 0, "max":          0},
                       "OUTPUT_MUX_SELECT": {"addr":         1, "loc":  0, "mask":     0xFFFF, "regs":   1, "min": 0, "max":          2},
                  "POST_PROCESSING_SELECT": {"addr":         1, "loc": 16, "mask": 0xFFFF0000, "regs":   1, "min": 0, "max":       0xFF},
                            "TRIGGER_TYPE": {"addr":         2, "loc":  0, "mask": 0xFFFFFFFF, "regs":   1, "min": 0, "max": 0xFFFFFFFF},
                     "SERIAL_READOUT_TYPE": {"addr":         3, "loc":  0, "mask": 0xFFFFFFFF, "regs":   1, "min": 0, "max": 0xFFFFFFFF},
         "TRIGGER_ENERGY_INTEGRATION_TIME": {"addr":         4, "loc":  0, "mask": 0xFFFFFFFF, "regs":   1, "min": 0, "max": 0xFFFFFFFF},
              "PIXELS_DARK_COUNT_RESET_EN": {"addr":         5, "loc":  0, "mask":        0x1, "regs":   1, "min": 0, "max":          1},
                   "READ_UNTRIGGERED_TDCS": {"addr":         5, "loc":  1, "mask":        0x2, "regs":   1, "min": 0, "max":          1},
   "TRIGGER_EVENT_DRIVEN_COLUMN_THRESHOLD": {"addr":         6, "loc":  0, "mask": 0xFFFFFFFF, "regs":   1, "min": 0, "max": 0xFFFFFFFF},
              "TRIGGER_TIME_DRIVEN_PERIOD": {"addr":         7, "loc":  0, "mask": 0xFFFFFFFF, "regs":   1, "min": 0, "max": 0xFFFFFFFF},
         "TRIGGER_WINDOW_DRIVEN_THRESHOLD": {"addr":         8, "loc":  0, "mask": 0xFFFFFFFF, "regs":   1, "min": 0, "max": 0xFFFFFFFF},
                            "READOUT_MODE": {"addr":         9, "loc":  0, "mask": 0xFFFFFFFF, "regs":   1, "min": 0, "max": 0xFFFFFFFF},
                         "TDC_GATING_MODE": {"addr":        10, "loc":  0, "mask": 0xFFFFFFFF, "regs":   1, "min": 0, "max": 0xFFFFFFFF},
                       "TIME_BIN_BOUNDS_0": {"addr":        11, "loc":  0, "mask":     0xFFFF, "regs":   1, "min": 0, "max":     0xFFFF},
                     "TIME_BIN_BOUNDS_0_1": {"addr":        11, "loc": 16, "mask": 0xFFFF0000, "regs":   1, "min": 0, "max":     0xFFFF},
                     "TIME_BIN_BOUNDS_1_2": {"addr":        12, "loc":  0, "mask":     0xFFFF, "regs":   1, "min": 0, "max":     0xFFFF},
                       "TIME_BIN_BOUNDS_2": {"addr":        12, "loc": 16, "mask": 0xFFFF0000, "regs":   1, "min": 0, "max":     0xFFFF},
                         "TDC_STOP_SIGNAL": {"addr":        13, "loc":  0, "mask": 0xFFFFFFFF, "regs":   1, "min": 0, "max": 0xFFFFFFFF},
                              "DCA_ENABLE": {"addr":        14, "loc":  0, "mask":        0x1, "regs":   1, "min": 0, "max":          1},
                           "DCA_THRESHOLD": {"addr":        14, "loc":  1, "mask":       0x1E, "regs":   1, "min": 0, "max":         15},
                         "PLL_ENABLE_TEST": {"addr":        15, "loc":  0, "mask":        0x1, "regs":   1, "min": 0, "max":          1},
                         "PLL_SELECT_TEST": {"addr":        15, "loc":  1, "mask":        0x2, "regs":   1, "min": 0, "max":          1},
            "PLL_DISABLE_EXTERNAL_TRIGGER": {"addr":        15, "loc":  2, "mask":        0x4, "regs":   1, "min": 0, "max":          1},
                        "PLL_SFTWR_RST_EN": {"addr":        15, "loc":  3, "mask":        0x8, "regs":   1, "min": 0, "max":          1},
                           "PLL_SFTWR_RST": {"addr":        15, "loc":  4, "mask":       0x10, "regs":   1, "min": 0, "max":          1},
                              "PLL_ENABLE": {"addr":        15, "loc":  5, "mask":       0x20, "regs":   1, "min": 0, "max":          1},
                    "PLL_TEST_SECTION_MUX": {"addr":        15, "loc": 16, "mask": 0xFFFF0000, "regs":   1, "min": 0, "max":     0xFFFF},
                      "DCR_INTERVAL_WIDTH": {"addr":        16, "loc":  0, "mask": 0xFFFFFFFF, "regs":   1, "min": 0, "max": 0xFFFFFFFF},
                    "DCR_INTERVAL_SPACING": {"addr":        17, "loc":  0, "mask": 0xFFFFFFFF, "regs":   1, "min": 0, "max": 0xFFFFFFFF},
                   "WINDOW_BIT_CONFIG_LOW": {"addr":        18, "loc":  0, "mask": 0xFFFFFFFF, "regs":   1, "min": 0, "max":          1},
                  "WINDOW_BIT_CONFIG_HIGH": {"addr":        18, "loc":  7, "mask":       0X80, "regs":   1, "min": 0, "max":          1},
               "WINDOW_BIT_REF_CONFIG_LOW": {"addr":        18, "loc":  8, "mask":      0x100, "regs":   1, "min": 0, "max":          1},
              "WINDOW_BIT_REF_CONFIG_HIGH": {"addr":        18, "loc":  9, "mask":     0x8000, "regs":   1, "min": 0, "max":          1},
                  "INDIVIDUAL_SPAD_ACCESS": {"addr":        19, "loc":  0, "mask": 0xFFFFFFFF, "regs":   1, "min": 0, "max": 0xFFFFFFFF},
    "EVENT_DETECTION_BIT_INTEGRATION_TIME": {"addr":        20, "loc":  0, "mask":        0x1, "regs":   1, "min": 0, "max":          1},
    "EVENT_DETECTION_BIT_COLUMN_THRESHOLD": {"addr":        20, "loc": 12, "mask":     0x1000, "regs":   1, "min": 0, "max":          1},
    "ENERGY_DISCRIMINATION_TIME_THRESHOLD": {"addr":        21, "loc":  0, "mask":     0xFFFF, "regs":   1, "min": 0, "max":     0xFFFF},
      "ENERGY_DISCRIMINATION_PHOTON_ORDER": {"addr":        21, "loc": 16, "mask":   0x3F0000, "regs":   1, "min": 0, "max":       0x3F},
     "ENERGY_DISCRIMINATION_ALWAYS_OUTPUT": {"addr":        21, "loc": 22, "mask":   0x400000, "regs":   1, "min": 0, "max":          1},

               "PIXEL_DISABLE_TDC_ARRAY_0": {"addr":        22, "loc":  0, "mask": 0xFFFFFFFF, "regs":   2, "min": 0, "max": 0xFFFFFFFF},
            "PIXEL_DISABLE_QUENCH_ARRAY_0": {"addr":        24, "loc":  0, "mask": 0xFFFFFFFF, "regs":   7, "min": 0, "max": 0xFFFFFFFF},
        "DISABLE_EXTERNAL_TRIGGER_ARRAY_0": {"addr":        31, "loc":  0, "mask": 0xFFFFFFFF, "regs":   7, "min": 0, "max": 0xFFFFFFFF},
          "TIME_CONVERSION_CLOCK_PERIOD_0": {"addr":        38, "loc":  0, "mask": 0xFFFFFFFF, "regs":   1, "min": 0, "max": 0xFFFFFFFF},
           "DARK_COUNT_FILTER_DELTA_0_1_0": {"addr":        40, "loc":  0, "mask": 0xFFFFFFFF, "regs":   1, "min": 0, "max": 0xFFFFFFFF},
           "DARK_COUNT_FILTER_DELTA_2_3_0": {"addr":        41, "loc":  0, "mask": 0xFFFFFFFF, "regs":   1, "min": 0, "max": 0xFFFFFFFF},
           "DARK_COUNT_FILTER_DELTA_4_5_0": {"addr":        42, "loc":  0, "mask": 0xFFFFFFFF, "regs":   1, "min": 0, "max": 0xFFFFFFFF},
             "REGISTER_WEIGHTED_AVERAGE_0": {"addr":        43, "loc":  0, "mask": 0xFFFFFFFF, "regs":  16, "min": 0, "max": 0xFFFFFFFF},
              "COARSE_BIAS_LOOKUP_TABLE_0": {"addr":        59, "loc":  0, "mask": 0xFFFFFFFF, "regs": 196, "min": 0, "max": 0xFFFFFFFF},
             "COARSE_SLOPE_LOOKUP_TABLE_0": {"addr":       255, "loc":  0, "mask": 0xFFFFFFFF, "regs":  98, "min": 0, "max": 0xFFFFFFFF},
                       "SPAD_LOCAL_SKEW_0": {"addr":       353, "loc":  0, "mask": 0xFFFFFFFF, "regs":  98, "min": 0, "max": 0xFFFFFFFF},
             "TDC_LOCAL_CORRECTION_FINE_0": {"addr":       451, "loc":  0, "mask": 0xFFFFFFFF, "regs":  25, "min": 0, "max": 0xFFFFFFFF},
           "TDC_LOCAL_CORRECTION_COARSE_0": {"addr":       476, "loc":  0, "mask": 0xFFFFFFFF, "regs":  25, "min": 0, "max": 0xFFFFFFFF},

               "PIXEL_DISABLE_TDC_ARRAY_1": {"addr":  22+M_OFS, "loc":  0, "mask": 0xFFFFFFFF, "regs":   2, "min": 0, "max": 0xFFFFFFFF},
            "PIXEL_DISABLE_QUENCH_ARRAY_1": {"addr":  24+M_OFS, "loc":  0, "mask": 0xFFFFFFFF, "regs":   7, "min": 0, "max": 0xFFFFFFFF},
        "DISABLE_EXTERNAL_TRIGGER_ARRAY_1": {"addr":  31+M_OFS, "loc":  0, "mask": 0xFFFFFFFF, "regs":   7, "min": 0, "max": 0xFFFFFFFF},
          "TIME_CONVERSION_CLOCK_PERIOD_1": {"addr":  38+M_OFS, "loc":  0, "mask": 0xFFFFFFFF, "regs":   1, "min": 0, "max": 0xFFFFFFFF},
           "DARK_COUNT_FILTER_DELTA_0_1_1": {"addr":  40+M_OFS, "loc":  0, "mask": 0xFFFFFFFF, "regs":   1, "min": 0, "max": 0xFFFFFFFF},
           "DARK_COUNT_FILTER_DELTA_2_3_1": {"addr":  41+M_OFS, "loc":  0, "mask": 0xFFFFFFFF, "regs":   1, "min": 0, "max": 0xFFFFFFFF},
           "DARK_COUNT_FILTER_DELTA_4_5_1": {"addr":  42+M_OFS, "loc":  0, "mask": 0xFFFFFFFF, "regs":   1, "min": 0, "max": 0xFFFFFFFF},
             "REGISTER_WEIGHTED_AVERAGE_1": {"addr":  43+M_OFS, "loc":  0, "mask": 0xFFFFFFFF, "regs":  16, "min": 0, "max": 0xFFFFFFFF},
              "COARSE_BIAS_LOOKUP_TABLE_1": {"addr":  59+M_OFS, "loc":  0, "mask": 0xFFFFFFFF, "regs": 196, "min": 0, "max": 0xFFFFFFFF},
             "COARSE_SLOPE_LOOKUP_TABLE_1": {"addr": 255+M_OFS, "loc":  0, "mask": 0xFFFFFFFF, "regs":  98, "min": 0, "max": 0xFFFFFFFF},
                       "SPAD_LOCAL_SKEW_1": {"addr": 353+M_OFS, "loc":  0, "mask": 0xFFFFFFFF, "regs":  98, "min": 0, "max": 0xFFFFFFFF},
             "TDC_LOCAL_CORRECTION_FINE_1": {"addr": 451+M_OFS, "loc":  0, "mask": 0xFFFFFFFF, "regs":  25, "min": 0, "max": 0xFFFFFFFF},
           "TDC_LOCAL_CORRECTION_COARSE_1": {"addr": 476+M_OFS, "loc":  0, "mask": 0xFFFFFFFF, "regs":  25, "min": 0, "max": 0xFFFFFFFF}

}

    ADDRESS_INFO = []
    GPIO_PINS = {}

    def __init__(self, DLLName="icyshsr1-lib.so", name="ICYSHSR1"):
        self.__dict__ = {}
        self._name = name
        try:
            self.libc = CDLL(DLLName)
        except Exception as e:
            self.libc = None
            _logger.error("Could not find DLL " + str(DLLName) + ". Thus, could not properly create device.")
        self.from_dict_plat()

    def from_dict_plat(self):
        for key, value in self.REGISTERS_INFO.items():
            value = Command(value, str(key), self)
            self.__dict__[key] = value

    def register_device(self, devNum):
        self.ADDRESS_INFO.append({'devNum': devNum})
        _logger.debug("Added ICYSHSR1 device with devNum: " + str(devNum))

    def device_summary(self):
        report = ""
        for addr in self.ADDRESS_INFO:
            report += ('{DeviceName: <10} :: devNum:{devNum: >3}\n'.format(
                DeviceName=self._name, devNum=addr['devNum']))
        return report

    def __repr__(self):
        return self._name

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]


    def read_param(self, devNum, paramName, register_offset=0):
        if not (paramName in self.REGISTERS_INFO):
            _logger.error(str(paramName) + " is an invalid parameter name")
            return -1

        paramInfo = self.REGISTERS_INFO[paramName]

        if register_offset > paramInfo['regs'] - 1:
            _logger.error("Offset too high, aborting...")
            return -1

        ic_dev_num = self.ADDRESS_INFO[devNum]['devNum']

        retval = c_ulonglong(0)
        try:
            retval = self.libc.ic_read(c_ushort(ic_dev_num), c_ulonglong(paramInfo['addr'] + register_offset), c_ushort(0))
        except Exception as e:
            _logger.error("could not read from IC:")
            _logger.error(e)
            return -1

        return retval

    def write_param(self, devNum, paramName, value, register_offset=0):
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

        if (0 == paramInfo["min"]) and (0 == paramInfo["max"]):
            _logger.error(str(paramName) + " is a read-only parameter")
            return -1

        if (value < paramInfo["min"]) or (value > paramInfo["max"]):
            _logger.error(
                "{value} is an invalid value for {paramName}. Must be between {min} and {max}".format(value=value,
                                                                                                      paramName=paramName,
                                                                                                      min=paramInfo[
                                                                                                          "min"],
                                                                                                      max=paramInfo[
                                                                                                          "max"]))
            return -1

        paramInfo = self.REGISTERS_INFO[paramName]

        if register_offset > paramInfo['regs'] - 1:
            _logger.error("Offset too high, aborting...")
            return -1


        # Positions to appropriate bits
        value <<= paramInfo["loc"]
        # Restrain to concerned bits
        value &= paramInfo["mask"]

        value = self.register_exceptions(paramInfo, value)

        #Convert to 64 bits here, just in case
        value = c_ulonglong(value)
        #Add register address
        value += c_longlong(paramInfo['addr'] + register_offset) << 32

        ic_dev_num = self.ADDRESS_INFO[devNum]['devNum']
        self.libc.ic_write(c_ushort(ic_dev_num), c_ulonglong(value))

        return 0

    # Here are all the formatting exceptions for registers.
    def PLL_ENABLE_TEST(self, paramInfo, value):
        return value

    def selftest(self, devNum):

        if self.libc == None:
            _logger.warning("No LIBC registered for ICYSHSR1, skipping")
            return -1

        ic_dev_num = self.ADDRESS_INFO[devNum]['devNum']

        # Selftest the AXI IP first
        try:
            retVal = self.libc.axi_selftest(c_ushort(ic_dev_num))
        except Exception as e:
            _logger.error("Could not open axi device")
            _logger.error(e)
            return -1

        if (retVal != 0xDEADBEEF):
            _logger.error("Self-test of the AXI IP for the ICYSHSR1 #" + str(ic_dev_num) + " failed. Check your connection...")
            _logger.error("Expecting: " + str(0xDEADBEEF) + ", Received: " + str(retVal))
            return -1

        # Selftest the ASIC itself now
        register_address = self.REGISTERS_INFO['ASIC_ID']['addr']
        retVal = self.libc.ic_read(c_ushort(ic_dev_num), c_ulonglong(register_address), c_ushort(0x0))

        if (retVal != 0xF0E32001):
            _logger.error("Self-test of the ASIC ICYSHSR1 #" + str(ic_dev_num) + " failed. Check your connection...")
            _logger.error("Expecting: " + str(0xF0E32001) + ", Received: " + str(retVal))
            return -1

        return 0

    def readout_all_registers(self, devNum):
        ic_dev_num = self.ADDRESS_INFO[devNum]['devNum']

        _logger.info("==== Device report ====")
        _logger.info("Device Name: " + str(self.DEVICE_NAME))
        _logger.info("DevNum: " + str(ic_dev_num))
        for paramName in self.REGISTERS_INFO:
            for reg in range(self.REGISTERS_INFO[paramName]['regs']):
                val = self.read_param(ic_dev_num, paramName, register_offset=reg)
                _logger.info('Param Name: {ParamName: <20}, Register Offset: {regOffset: <4}, Param Value: {Value: <16}'.format(ParamName=paramName, regOffset=reg, Value=val))

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
                self._acc.read_param(args[0], self._name, args[1])
            elif len(args) == 3:
                self._acc.write_param(args[0], self._name, args[1], args[2])
            else:
                _logger.warning("Incorrect number of arguments. Ignoring")
        except Exception as e:
            _logger.error("Could not set message to device. Check connection...")
            _logger.error(e)

    def from_dict(self, d, name=""):
        for key, value in d.items():
            self.__dict__[key] = value

    def __repr__(self):
        return self._name

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]


