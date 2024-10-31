from abc import ABC, abstractmethod
from typing import Type
from Setting import *
from Utils import *

#enum display
IDP_BUTTON = 0x01
IDP_INPUT = 0x02
IDP_TEXT = 0x03
IDP_FRAME = 0x04

class PreLayoutElement(ABC):
    def __init__(self, type, name="", key=None, ret:Pointer=None) -> None:
        self.__type = type
        self.__name = name
        self.__key = key
        self.__ret = ret

    def GetType(self):
        return self.__type
    
    def GetName(self):
        return self.__name
    
    def GetKey(self):
        return self.__key
    
    def GetRet(self):
        return self.__ret

class IDisplay(ABC):
    def __init__(self) -> None:
        self.__slaveSettings = dict

    def SetSlaveSettingsRef(self, slaveSettings:dict) -> None:
        self.__slaveSettings = slaveSettings

    def GetSlaveSettings(self) -> dict:
        return self.__slaveSettings

    @abstractmethod
    def Update(self) -> Setting:
        pass

    @abstractmethod
    def UpdateLayout(self, slaveSettings:dict) -> None:
        pass

    @abstractmethod
    def UpdateSetting(self,setting:Setting) -> None:
        pass