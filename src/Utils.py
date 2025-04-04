
from typing import Any


class Mutable:
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
    
    def __add__(self, other):
        return Mutable(self.__value + other)
    
    def __sub__(self, other):
        return Mutable(self.__value + other)
    
    def __iadd__(self, other):
        self.__value += other
        return self
    
    def __isub__(self, other):
        self.__value -= other
        return self
    
    def __mul__(self, other):
        return Mutable(self.__value * other)
    
    def __imul__(self, other):
        self.__value *= other
        return self
    
    def __truediv__(self, other):
        return Mutable(self.__value / other)
    
    def __itruediv__(self, other):
        self.__value /= other
        return self
    
    def __eq__(self, other):
        return self.__value == other
    
    def __gt__(self, other):
        return self.__value > other
    
    def __lt__(self, other):
        return self.__value < other
    
    def __ne__(self, other):
        return self.__value != other
    
    def __ge__(self, other):
        return self.__value >= other
    
    def __le__(self, other):
        return self.__value <= other
    
    def __str__(self):
        return str(self.__value)