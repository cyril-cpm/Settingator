from abc import ABC, abstractmethod
from typing import Type
from Utils import *
import weakref

#enum display
IDP_NONE = 0x00
IDP_BUTTON = 0x01
IDP_INPUT = 0x02
IDP_TEXT = 0x03
IDP_FRAME = 0x04
IDP_COLUMN = 0x05
IDP_CHECK = 0x06
IDP_SLIDER = 0x07

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
    def __init__(self):
        pass

    def __del__(self):
        pass

    @abstractmethod
    def SetBGColor(self, color):
        pass

    @abstractmethod
    def UpdateValue(self, value):
        pass

    @abstractmethod
    def GetValue(self):
        pass

    @abstractmethod
    def GetElement(self):
        pass

    @abstractmethod
    def SetEnable(self, value:bool):
        pass

    @abstractmethod
    def SetVisible(self, value):
        pass


class LayoutElement(ABC):
    def __init__(self, type, value=None, name="", children:list=None, callback=None) -> None:
        self.__type = type
        self.__name = name
        self.__value = value
        self.__parent:LayoutElement = None
        self.__isModified = True
        self.__isNew = True
        self.__callback = callback

        self.__iElement:IElement = None

        self.__children:list = children

        if isinstance(self.__children, list):
            for element in self.__children:
                if element:
                    element.SetParentRecursively(self)

        if (type == IDP_COLUMN or type == IDP_FRAME) and children == None:
            self.__children = []

    def __del__(self):
        pass

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
    
    def GetValue(self):
        return self.__value
    
    def SetValue(self, value):
        self.__value = value

    def UpdateValue(self, value):
        self.SetValue(value)
        
        if not self.IsNew():
            self.__iElement.UpdateValue(value)
    
    def GetChildren(self):
        return self.__children
    
    def GetIElement(self) -> IElement:
        return self.__iElement
    
    def SetIElement(self, element:IElement) -> None:
        self.__iElement = element

    def SetParent(self, parent = None) -> None:
        if parent == None:
            self.__parent = None
        else:
            self.__parent = weakref.ref(parent)

    def SetParentRecursively(self, parent = None) -> None:
        if parent != None:
            self.__parent = weakref.ref(parent)
        else:
            self.__parent = None

        if isinstance(self.__children, list):
            for element in self.__children:
                element.SetParentRecursively(self)
    
    def GetParent(self):
        if self.__parent:
            return self.__parent()
        return self.__parent
    
    def SetModified(self, modified:bool = True):
        self.__isModified = modified


        if modified and self.__parent and self.__parent():
            self.__parent().SetModified()

    def IsModified(self) -> bool:
        return self.__isModified
    
    def AppendElement(self, element) -> None:
        if isinstance(self.__children, list):
            self.__children.append(element)
            element.SetParent(self)

            #self.__toAddInView.append(element)
            self.SetModified()
            
        else:
            print("Can't append element to " + IDPTypeToStr(self.__type) + ", name is \"" + self.__name + "\"")
            print("children:")
            print(str(self.__children))

    def RemoveElement(self, element) -> None:
        if isinstance(self.__children, list):

            if element in self.__children:
                self.SetModified()
                element.SetParent()
                self.__children.remove(element)
                
                #self.__toRemoveFromView.append(str(element))
        else:
            print("Can't remove element to " + IDPTypeToStr(self.__type) + ", name is \"" + self.__name + "\"")
            print("children:")
            print(str(self.__children))

    def Call(self, value = None):
        if self.__callback != None:
            self.__callback(value)

    def SetEnable(self, value):
        self.__iElement.SetEnable(value)

        if isinstance(self.__children, list):
            for children in self.__children:
                children.SetEnable(value)

    def SetVisible(self, value):
        self.__iElement.SetVisible(value)

class IDisplay(ABC):
    def __init__(self) -> None:
        self.__slaveSettings = dict
        self._Layout = LayoutElement(IDP_COLUMN)
        self._isRunning = True

    def SetSlaveSettingsRef(self, slaveSettings:dict) -> None:
        self.__slaveSettings = slaveSettings

    def GetSlaveSettings(self) -> dict:
        return self.__slaveSettings

    @abstractmethod
    def Update(self) -> None:
        pass

    @abstractmethod
    def UpdateLayout(self) -> None:
        pass

    @abstractmethod
    def IsRunning(self) -> bool:
        pass

    def AddLayout(self, element:LayoutElement) -> None:
        self._Layout.AppendElement(element)

    def RemoveLayout(self, element:LayoutElement) -> None:
        self._Layout.RemoveElement(element)

    def GetLayout(self) -> list:
        return self._Layout
