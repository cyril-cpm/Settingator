from abc import ABC, abstractmethod
from typing import Type
from enum import Enum

class SettingType(Enum):
    SLIDER = 1
    TRIGGER = 2
    SWITCH = 3
    LABEL = 4

def IsNumericalTypeValue(settingType:int) -> bool:
    if (settingType == SettingType.SLIDER.value):
        return True
    
    if (settingType == SettingType.TRIGGER.value):
        return True
    
    if (settingType == SettingType.SWITCH.value):
        return True

def GetNumericalValueFromBuffer(value:bytearray) -> tuple:
    valueLen = value.__len__()

    retValue = 0
    index = 0
    while (index != valueLen):        
        retValue = retValue << 8
        retValue = value[index]
        index += 1
    
    return (retValue, valueLen)

def GetStringValueFromBuffer(value:bytearray) -> tuple:
    string = str()
    strLen = value.__len__()
    index = 0
    while(index != strLen):
        string += chr(value[index])
        index += 1

    return (string, strLen)

class Setting():
    def __init__(self, ref:int, slaveID:int = 0, name:str = '', type:int = 0, value:bytearray = 0) -> None:
        self.__ref = ref
        self.__name = name
        self.__type = type
        self.__slaveID = slaveID

        if (IsNumericalTypeValue(type)):
            self.__value, self.__valueLen = GetNumericalValueFromBuffer(value)
        else:
            self.__value, self.__valueLen = GetStringValueFromBuffer(value)

    def GetName(self):
        return self.__name

    def GetValue(self):
        return self.__value

    def GetValueLen(self):
        return self.__valueLen

    def GetRef(self):
        return self.__ref

    def GetType(self):
        return self.__type
    
    def GetSlaveID(self):
        return self.__slaveID

    def SetValue(self, value):
        if (IsNumericalTypeValue(self.__type)):
            self.__value = int(value)

