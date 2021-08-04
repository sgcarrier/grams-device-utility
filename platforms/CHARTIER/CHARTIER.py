import json
from pkg_resources import resource_filename
import importlib
import logging
from devices.remoteCommand import *
import sys, time, os

_logger = logging.getLogger(__name__)


class CHARTIER():

    def __init__(self, layoutFile=None, name="CHARTIER", logPath="log/", remoteIP=None):
        if layoutFile is None:
            layoutFile = resource_filename(__name__, 'device_layout.json')

        with open(layoutFile, 'r') as f:
            self.layout = json.load(f)

        self.remoteIP = remoteIP

        self._name = name
        self._remoteIP = remoteIP
        self.from_dict_layout(self.layout)
        _logger.info(self.layout2Report(self.layout, name))


    def from_dict_layout(self, d):

        if self._remoteIP:
            cmdClass = partialCommand(RemoteCommand, ip=self._remoteIP, port=5000, timeout=None)
        else:
            cmdClass = None

        for manu, dev in d.items():
            for devName, attr in dev.items():
                moduleName = "devices." + manu + "." + devName
                devClass = self.class_for_name(moduleName, devName)
                # independent here means that there is local data to be maintained for each device,
                # so all instances should be separate
                if attr['independent'] == False:
                    self.__dict__[devName] = devClass(cmdClass=cmdClass)
                    if "ADDRESS_INFO" in attr:
                        self.__dict__[devName].ADDRESS_INFO = attr["ADDRESS_INFO"]
                    if "GPIO_PINS" in attr:
                        self.__dict__[devName].GPIO_PINS = attr["GPIO_PINS"]
                    if hasattr(self.__dict__[devName], 'setup'):
                        self.__dict__[devName].setup()
                    
                else:
                    num = 0
                    if "ADDRESS_INFO" in attr:
                        for addr_info in attr["ADDRESS_INFO"]:
                            self.__dict__[devName+"_"+str(num)] = devClass(cmdClass=cmdClass)
                            self.__dict__[devName+"_"+str(num)].ADDRESS_INFO = addr_info
                            self.__dict__[devName + "_" + str(num)].DEVICE_NAME = devName+"_"+str(num)
                            num += 1

                    num = 0
                    if "GPIO_PINS" in attr:
                        for gpio_pins in attr["GPIO_PINS"]:
                            self.__dict__[devName+"_"+str(num)].GPIO_PINS = gpio_pins
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
            if hasattr(item, "DEVICE_NAME"):
                devNum = 0
                if item.ADDRESS_INFO:
                    for addr in item.ADDRESS_INFO:
                        _logger.debug(addr)
                        ret = item.selftest(devNum)
                        report += '{DeviceName: <10} :: '.format(DeviceName=item.DEVICE_NAME)
                        report += self.dict2str(addr)
                        if ret == 0:
                            report += " ... PASSED \n"
                            passed += 1
                        elif ret == 1:
                            report += " ... SKIPPED \n"
                            passed += 1
                        else:
                            report += " ... FAILED \n"
                            failed += 1
                        devNum += 1
        report += "\n============ SELFTEST SUMMARY ============\n"
        report += 'PASSED: {Passed: <10}'.format(Passed=passed)
        report += 'FAILED: {Failed: <10}'.format(Failed=failed)
        report += "\n========== DEVICE SELFTEST DONE ==========\n"

        _logger.info(report)


    def class_for_name(self, module_name, class_name):
        try:
            # load the module, will raise ImportError if module cannot be loaded
            m = importlib.import_module(module_name)
            # get the class, will raise AttributeError if class cannot be found
            c = getattr(m, class_name)
            return c
        except ImportError:
            _logger.error(module_name)
            _logger.error("Error, could not import module from string")
            return None
        except AttributeError:
            _logger.error("Error, could not import class from string")
            return None

    def dict2str(self, d):
        s = ""
        for key, item in d.items():
            s += '{keyName: <10}: {value: <20},'.format(keyName=key, value=item)
        return s[0:-2]

    def layout2Report(self, layout, boardName):
        report = "\n========== DEVICE LAYOUT REPORT ==========\n"
        report += "Board Name : {BoardName: <20} \n".format(BoardName=boardName)
        report += '-' * 80 + "\n"
        for devName, dev in self.__dict__.items():
            if hasattr(dev, "device_summary"):
                report += dev.device_summary()
                report += '-' * 80 + "\n"
        # for manu, dev in layout.items():
        #     for devName, attr in dev.items():
        #         report += attr.device_summary()
        #         report += '-' * 30 + "\n"
        #         # if 'ADDRESS_INFO' in attr:
        #         #     for addr in attr['ADDRESS_INFO']:
        #         #         if "ch" in addr:
        #         #             report += ('{DeviceName: <10} :: Channel:{Channel: >3}, Address:{Address: >4}(0x{Address:02X})\n'.format(DeviceName=devName, Channel=addr['ch'], Address=addr['addr']))
        #         #         elif "path" in addr:
        #         #             report += ('{DeviceName: <10} :: Path:{Path: >3}, Mode:{Mode: >4}(0x{Mode:02X})\n'.format(DeviceName=devName, Path=addr['path'], Mode=addr['mode']))
        #         #     report += '-' * 30 + "\n"
        #         # else:
        #         #     report += ('{DeviceName: <10} :: [N/A])\n'.format(DeviceName=devName))
        #         #     report += '-' * 30 + "\n"

        return report

if __name__ == "__main__":

    import sys
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)

    b = CHARTIER(remoteIP="192.168.0.200")

    test = b.LMK03318.VNDRID(0)
    print(test)
