import time
import logging
import requests
import functools
import json

_logger = logging.getLogger(__name__)

def partialCommand(cls, *args, **kwds):

    class NewCls(cls):
        __init__ = functools.partialmethod(cls.__init__, *args, **kwds)

    return NewCls


class RemoteCommand:
    """
    This class allows us to use all registers as attributes. Calling this will send the equivalent command to  the
    target machine on the network
    For example:
       > d = Device()
       > d.register_name(0)  # read operation of the device number 0
       > d.register_name(0, 1) # writing 1 to the device 0
    """

    def __init__(self, d, name="", acc=None, ip="192.168.0.200", port=5000, timeout=None):
        self.__dict__ = {}
        self._name = name
        self._acc = acc
        self._deviceName = d

        self.IP = ip
        self.port = port
        self._url = "http://" + str(self.IP) + ":" + str(port)
        self.timeout = timeout

    def __call__(self, *args):

        dest = self._url + "/" + str(self._acc._name) + "/" + str(self._name)

        if (self._name == "GPIO"):
            if len(args) == 3:
                params = {"devNum": args[0], "name": args[1], "value": args[2]}
                r = requests.post(dest, params=params, timeout=self.timeout)
            else:
                _logger.warning("Incorrect number of arguments. Ignoring")

        if (self._name == "SELFTEST"):
            if len(args) == 1:
                params = {"devNum": args[0]}
                r = requests.get(dest, params=params, timeout=self.timeout)
                return json.loads(r.content)['returnValue']
            else:
                _logger.warning("Incorrect number of arguments. Ignoring")

        # TODO find a solution to this exception case
        if (self._acc._name != "ICYSHSR1"):
            if len(args) == 2:
                params = {"devNum": args[0], "value": args[1]}
                r = requests.get(dest, params=params, timeout=self.timeout)
                return json.loads(r.content)['returnValue']
            elif len(args) == 3:
                params = {"devNum": args[0], "value": args[1], "register_offset": args[2]}
                r = requests.post(dest, params=params, timeout=self.timeout)
            else:
                _logger.warning("Incorrect number of arguments. Ignoring")
        else:
            if len(args) == 2:
                params = {"devNum": args[0], "value": args[1]}
                r = requests.post(dest, params=params, timeout=self.timeout)
            elif len(args) == 1:
                params = {"devNum": args[0]}
                r = requests.get(dest, params=params, timeout=self.timeout)
                return json.loads(r.content)['returnValue']
            else:
                _logger.warning("Incorrect number of arguments. Ignoring")

        time.sleep(0.01)

    def __repr__(self):
        return self._name

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]
