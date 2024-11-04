
from typing import Any


class Pointer:
    def __init__(self, value=None):
        self.__value = value

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.__value

    def __del__(self):
        self.__value = None

    def SetValue(self, value):
        self.__value = value

    def GetValue(self):
        return self.__value