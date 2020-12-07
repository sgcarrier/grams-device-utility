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
                self.__dict__[devName] = devClass()
                self.__dict__[devName].ADDRESS_INFO = attr["addr"]
                if "GPIO_PINS" in attr:
                    self.__dict__[devName].GPIO_PINS = attr["GPIO_PINS"]

    def __repr__(self):
        return self._name

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]


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