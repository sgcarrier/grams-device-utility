import requests


# class RemoteAccessor():
#
#     def __init__(self, name):
#         self._name = name
#
#     def write_param(self, **kwargs):
#         pass
#
#     def read_param(self, **kwargs):
#         pass


class RemoteAccessor():

    def __init__(self, boardName=None, deviceName=None, ip="192.168.1.10", port=5000, timeout=None):
        self.IP = ip
        self.port = port
        self._url = "http://" + str(self.IP) + ":" + str(port)
        self.timeout = timeout
        self.boardName = boardName
        self.deviceName = deviceName
        print("REMOTE ACCESSOR USED")

    def write_param(self, **kwargs):
        print("write_param " + str(kwargs))

    def read_param(self, a,b):
        print("read_param REMOTE")

    def gpio_set(self, **kwargs):
        print("gpio_set " + str(kwargs))

    def selftest(self, **kwargs):
        print("selftest " + str(kwargs))