from abc import ABC, abstractmethod
from typing import Type
from Setting import *
from Utils import *

#enum display
IDP_NONE = 0x00
IDP_BUTTON = 0x01
IDP_INPUT = 0x02
IDP_TEXT = 0x03
IDP_FRAME = 0x04
IDP_COLUMN = 0x05

def IDPTypeToStr(IDPType:int = IDP_NONE):
    if IDPType == IDP_NONE:
        return "IDP_NONE"
    elif IDPType == IDP_BUTTON:
        return "IDP_BUTTON"
    elif IDPType == IDP_INPUT:
        return "IDP_INPUT"
    elif IDPType == IDP_TEXT:
        return "IDP_TEXT"
    elif IDPType == IDP_FRAME:
        return "IDP_FRAME"
    elif IDPType == IDP_COLUMN:
        return "IDP_COLUMN"
    else:
        return "IDP_UNKNOWN"
        

class PreLayoutElement(ABC):
    def __init__(self, type, name="", key=None, ret:Pointer=None) -> None:
        self.__type = type
        self.__name = name

        self.__key = key

        if (type == IDP_COLUMN or type == IDP_FRAME) and key == None:
            self.__key = []

        self.__ret = ret

    def __del__(self):
        self.__key = None
        print("delete")

    def GetType(self):
        return self.__type
    
    def GetName(self):
        return self.__name
    
    def GetKey(self):
        return self.__key
    
    def GetRet(self):
        return self.__ret
    
    def AppendElement(self, element) -> None:
        if isinstance(self.__key, list):
            self.__key.append(element)
        else:
            print("Can't append element to " + IDPTypeToStr(self.__type) + ", name is \"" + self.__name + "\"")
            print("Key:")
            print(str(self.__key))


    def RemoveElement(self, element) -> None:
        if isinstance(self.__key, list):
            self.__key.remove(element)
        else:
            print("Can't remove element to " + IDPTypeToStr(self.__type) + ", name is \"" + self.__name + "\"")
            print("Key:")
            print(str(self.__key))

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