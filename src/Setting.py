from abc import ABC, abstractmethod
from typing import Type
from enum import Enum

class SettingType(Enum):
    SLIDER = 1
    TRIGGER = 2
    SWITCH = 3

def IsNumericalTypeValue(settingType:int) -> bool:
    if (settingType == SettingType.SLIDER.value):
        return True
    
    if (settingType == SettingType.TRIGGER.value):
        return True
    
    if (settingType == SettingType.SWITCH.value):
        return True

def GetNumericalValue(value:bytearray) -> int:
    valueLen = value.__len__()

    retValue = 0
    index = 0
    while (index != valueLen):        
        retValue = retValue << 8
        retValue = value[index]
        index += 1
    
    return retValue

def GetStringValue(value:bytearray) -> str:
    string = str()
    strLen = value.__len__()
    index = 0
    while(index != strLen):
        string += chr(value[index])
        index += 1

    return string

class Setting():
    def __init__(self, ref:int, name:str = '', type:int = 0, value:bytearray = 0) -> None:
        self.__ref = ref
        self.__name = name
        self.__type = type

        if (IsNumericalTypeValue(type)):
            self.__value = GetNumericalValue(value)
        else:
            self.__value = GetStringValue(value)

    def GetName(self):
        return self.__name

    def GetValue(self):
        return self.__value

    def GetRef(self):
        return self.__ref

    def GetType(self):
        return self.__type

    def SetValue(self, value:int):
        self.__value = value

class SettingList():
    def __init__(self) -> None:
        self.__settings = []

    def AddSetting(self, setting:Setting) -> None:
        self.__settings.append(setting)

    def GetSetting(self, index:int) -> Setting:
        return self.__settings[index]

    def GetSettingByRef(self, ref:int) -> Setting:
        index = 0
        size = self.GetSize()

        while (index < size):
            if (self.__settings[index].GetRef() == ref):
                return self.__settings[index]
            index += 1

    def GetSize(self) -> int:
        return self.__settings.__len__()

class SettingLayout():
    def __init__(self) -> None:
        self.__settingList = SettingList()

    def AddSetting(self, setting:Setting) -> None:
        self.__settingList.AddSetting(setting)

    def SetSettingList(self, settingList:SettingList) -> None:
        self.__settingList = settingList

    def GetSettingList(self) -> SettingList:
        return self.__settingList

    def SetSettingValue(self, ref:int, value:int) -> None:
        size = self.__settingList.GetSize()

        i = 0
        while (i < size):
            setting = self.__settingList.GetSetting(i)

            if (setting.GetRef() == ref):
                setting.SetValue(value)
                i = size

            i += 1