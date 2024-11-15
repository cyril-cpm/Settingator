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
        

class IElement(ABC):
    def __init__(self, value):
        self._value = value

    @abstractmethod
    def SetBGColor(self, color):
        pass

    @abstractmethod
    def UpdateValue(self, value):
        pass

class PreLayoutElement(ABC):
    def __init__(self, type, name="", key=None, ret:Pointer=None) -> None:
        self.__type = type
        self.__name = name
        self.__parent:PreLayoutElement = None
        self.__isModified = True
        self.__toRemoveFromView = []
        self.__toAddInView = []
        self.__isNew = True

        self.__key = key

        if (type == IDP_COLUMN or type == IDP_FRAME) and key == None:
            self.__key = []

        self.__ret = ret

    def __del__(self):
        self.__key = None
        print("delete")

    def IsNew(self):
        return self.__isNew
    
    def SetNew(self, value:bool):
        self.__isNew = value

    def GetElementsToRemoveFromView(self):
        return self.__toRemoveFromView
    
    def GetElementsToAddInView(self):
        return self.__toAddInView

    def GetType(self):
        return self.__type
    
    def GetName(self):
        return self.__name
    
    def GetKey(self):
        return self.__key
    
    def GetRet(self):
        return self.__ret
    
    def SetParent(self, parent = None) -> None:
        self.__parent = parent
    
    def GetParent(self):
        return self.__parent
    
    def SetModified(self, modified:bool = True):
        self.__isModified = modified


        if modified and self.__parent:
            self.__parent.SetModified()

    def IsModified(self) -> bool:
        return self.__isModified
    
    def AppendElement(self, element) -> None:
        if isinstance(self.__key, list):
            self.__key.append(element)
            element.SetParent(self)

            self.__toAddInView.append(element)
            self.SetModified()
            
        else:
            print("Can't append element to " + IDPTypeToStr(self.__type) + ", name is \"" + self.__name + "\"")
            print("Key:")
            print(str(self.__key))


    def RemoveElement(self, element) -> None:
        if isinstance(self.__key, list):

            if element in self.__key:
                element.SetParent()
                self.__key.remove(element)
                
                self.__toRemoveFromView.append(str(element))
                self.SetModified()
        else:
            print("Can't remove element to " + IDPTypeToStr(self.__type) + ", name is \"" + self.__name + "\"")
            print("Key:")
            print(str(self.__key))

class IDisplay(ABC):
    def __init__(self) -> None:
        self.__slaveSettings = dict
        self._PreLayout = PreLayoutElement(IDP_FRAME)

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

    @abstractmethod
    def IsRunning(self) -> bool:
        pass

    def AddPreLayout(self, element:PreLayoutElement) -> None:
        self._PreLayout.AppendElement(element)

    def RemovePreLayout(self, element:PreLayoutElement) -> None:
        self._PreLayout.RemoveElement(element)

    def GetPrelayout(self) -> list:
        return self._PreLayout