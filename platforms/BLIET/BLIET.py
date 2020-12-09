import json
from pkg_resources import resource_filename
import importlib
import logging

_logger = logging.getLogger(__name__)


class BLIET():

    def __init__(self, layoutFile=None, name="BLIET"):
        if layoutFile is None:
            layoutFile = resource_filename(__name__, 'device_layout.json')

        with open(layoutFile, 'r') as f:
            self.layout = json.load(f)

        self._name = name
        self.from_dict_layout(self.layout)
        _logger.info(self.layout2Report(self.layout, name))

    def from_dict_layout(self, d):
        for manu, dev in d.items():
            for devName, attr in dev.items():
                moduleName = "devices." + manu + "." + devName
                devClass = self.class_for_name(moduleName, devName)
                if attr['independent'] == False:
                    self.__dict__[devName] = devClass()
                    self.__dict__[devName].ADDRESS_INFO = attr["addr"]
                    if "GPIO_PINS" in attr:
                        self.__dict__[devName].GPIO_PINS = attr["GPIO_PINS"]
                else:
                    num = 0
                    for addr_info in attr["addr"]:
                        self.__dict__[devName+"_"+str(num)] = devClass()
                        self.__dict__[devName+"_"+str(num)].ADDRESS_INFO = addr_info
                        self.__dict__[devName + "_" + str(num)].DEVICE_NAME = devName+"_"+str(num)
                        if "GPIO_PINS" in attr:
                            self.__dict__[devName+"_"+str(num)].GPIO_PINS = attr["GPIO_PINS"][num]
                        num += 1

    def __repr__(self):
        return self._name

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]

    def runSelftests(self):
        report = "\n========== DEVICE SELFTEST REPORT ==========\n"
        report += "Board Name : {BoardName: <20} \n".format(BoardName=self._name)
        report += '-' * 30 + "\n"
        failed = 0
        passed = 0
        for key, item in self.__dict__.items():
            if item.DEVICE_NAME:
                devNum = 0
                for addr in item.ADDRESS_INFO:
                    ret = item.selftest(devNum)
                    report += '{DeviceName: <10} ::'.format(DeviceName=item.DEVICE_NAME)
                    report += self.dict2str(addr)
                    if ret == 0:
                        report += " ... PASSED \n"
                        passed += 1
                    else:
                        report += " ... FAILED \n"
                        failed += 1
                    devNum += 1
        report += "\n============ SELFTEST SUMMARY ============\n"
        report += 'PASSED: {Passed: <10}'.format(Passed=passed)
        report += 'FAILED: {Failed: <10}'.format(Failed=failed)
        report += "\n========== DEVICE SELFTEST DONE ==========\n"

    def class_for_name(self, module_name, class_name):
        try:
            # load the module, will raise ImportError if module cannot be loaded
            m = importlib.import_module(module_name)
            # get the class, will raise AttributeError if class cannot be found
            c = getattr(m, class_name)
            return c
        except ImportError:
            print(module_name)
            print("Error, could not import module from string")
            return None
        except AttributeError:
            print("Error, could not import class from string")
            return None

    def dict2str(self, d):
        s = ""
        for key, item in d.items:
            s += '{keyName: <10}: {value: <10},'.format(keyName=key, value=item)
        return s[0:-2]

    def layout2Report(self, layout, boardName):
        report = "\n========== DEVICE LAYOUT REPORT ==========\n"
        report += "Board Name : {BoardName: <20} \n".format(BoardName=boardName)
        report += '-' * 30 + "\n"
        for manu, dev in layout.items():
            for devName, attr in dev.items():
                for addr in attr['addr']:
                    report += ('{DeviceName: <10} :: Channel:{Channel: >3}, Address:{Address: >4}(0x{Address:02X})\n'.format(DeviceName=devName, Channel=addr['ch'], Address=addr['addr']))
                report += '-' * 30 + "\n"

        return report

if __name__ == "__main__":
    b = BLIET()

    test = b.LMK03318.LOL()