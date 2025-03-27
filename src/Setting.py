from abc import ABC, abstractmethod
from typing import Type
from enum import Enum
import struct

class SettingType(Enum):
    SLIDER = 1
    TRIGGER = 2
    SWITCH = 3
    LABEL = 4

    UINT32 = 0x20

    #TESTING 
    CUSTOM_FLOAT = 254

def IsNumericalTypeValue(settingType:int) -> bool:
    if (settingType == SettingType.SLIDER.value):
        return True
    
    if (settingType == SettingType.TRIGGER.value):
        return True
    
    if (settingType == SettingType.SWITCH.value):
        return True
    
    return False
    
def IsFloatTypeValue(settingType:int) -> bool:
    if (settingType == SettingType.CUSTOM_FLOAT.value):
        return True
    return False

def IsUInt32TypeValue(settingType:int) -> bool:
    return (settingType == SettingType.UINT32.value)

def GetNumericalValueFromBuffer(value:bytearray) -> tuple:
    valueLen = value.__len__()

    retValue = 0
    index = 0
    while (index != valueLen):        
        retValue = retValue << 8
        retValue = value[index]
        index += 1
    
    return (retValue, valueLen)

def GetFloatValueFromBuffer(value:bytearray) -> tuple:
    return(struct.unpack('<f', value)[0], value.__len__())

def GetUInt32ValueFromBuffer(value:bytearray) -> tuple:
    return(struct.unpack('<I', value)[0], value.__len__())

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
        elif (IsFloatTypeValue(type)):
            self.__value, self.__valueLen = GetFloatValueFromBuffer(value)
        elif (IsUInt32TypeValue(type)):
            self.__value, self.__valueLen = GetUInt32ValueFromBuffer(value)
        else:
            self.__value, self.__valueLen = GetStringValueFromBuffer(value)

    def GetName(self):
        return self.__name

    def GetValue(self):
        return self.__value
    
    def GetBinaryValue(self):
        
        if (IsFloatTypeValue(self.__type)):
            data = struct.pack("<f", self.__value)
            return data
        
        if (IsUInt32TypeValue(self.__type)):
            return struct.pack("<I", self.__value)

        if (IsNumericalTypeValue(self.__type)):
            return struct.pack("<B", self.__value)
        
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
        
        elif (IsFloatTypeValue(self.__type)):
            if value == '':
                value = 0.0
            self.__value = float(value)

        elif (IsUInt32TypeValue(self.__type)):
            if value == '':
                value = 0
            self.__value = int(value)

    def SetBinaryValue(self, value):
        if (IsNumericalTypeValue(self.__type)):
            self.__value = struct.unpack('<I', value)[0]

        elif (IsFloatTypeValue(self.__type)):
            self.__value = struct.unpack('<f', value)[0]

        elif (IsUInt32TypeValue(self.__type)):
            self.__value = struct.unpack('<I', value)[0]

    def AppendValueToBuffer(self, buffer:bytearray):
        value = self.GetBinaryValue()

        buffer.append(value.__len__())

        for i in range(0, value.__len__()):
            buffer.append(value[i])

