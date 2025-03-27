from abc import ABC, abstractmethod
from typing import Type
from enum import Enum
import struct
from Utils import *

class SettingType(Enum):
    SLIDER = 0x01
    TRIGGER = 0x02
    SWITCH = 0x03
    LABEL = 0x04

    UINT32 = 0x20
    UINT8 = 0x21
    UINT16 = 0x22
    FLOAT = 0x23
    BOOL = 0x24

    #TESTING 
    CUSTOM_FLOAT = 254

PACK_TAB = {
    SettingType.UINT8.value : '<B',
    SettingType.BOOL.value : '<B',
    SettingType.UINT16.value : '<H',
    SettingType.UINT32.value : '<I',
    SettingType.FLOAT.value : '<f'
}

def IsNumericalTypeValue(settingType:int) -> bool:
    return (settingType == SettingType.UINT8.value) or \
        (settingType == SettingType.UINT16.value) or \
        (settingType == SettingType.UINT32.value) or \
        (settingType == SettingType.FLOAT.value) or \
        (settingType == SettingType.BOOL.value)

def IsIntegerTypeValue(settingType:int) -> bool:
    return (settingType == SettingType.UINT8.value) or \
        (settingType == SettingType.UINT16.value) or \
        (settingType == SettingType.UINT32.value)

def IsFloatTypeValue(settingType:int) -> bool:
    return (settingType == SettingType.CUSTOM_FLOAT.value) or \
        (settingType == SettingType.FLOAT.value)

def IsBoolTypeValue(settingType:int) -> bool:
    return (settingType == SettingType.BOOL.value) or \
        (settingType == SettingType.SWITCH.value)

def IsUInt8TypeValue(settingType:int) -> bool:
    return (settingType == SettingType.UINT8.value)

def IsUInt16TypeValue(settingType:int) -> bool:
    return (settingType == SettingType.UINT16.value)

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
    return struct.unpack('<f', value)[0], value.__len__()

def GetBoolValueFromBuffer(value:bytearray) -> tuple:
    return struct.unpack('<B', value)[0], value.__len__()

def GetUInt8ValueFromBuffer(value:bytearray) -> tuple:
    return struct.unpack('<B', value)[0], value.__len__()

def GetUInt16ValueFromBuffer(value:bytearray) -> tuple:
    return struct.unpack('<H', value)[0], value.__len__()

def GetUInt32ValueFromBuffer(value:bytearray) -> tuple:
    return struct.unpack('<I', value)[0], value.__len__()

def GetNumeriacalValueFromBuffer(value:bytearray, type:SettingType):
    return struct.unpack(PACK_TAB[type], value)[0], value.__len__()

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
        self.__value = None
        self.__valueLen:int

        if (IsNumericalTypeValue(type)):
            self.__value, self.__valueLen = GetNumeriacalValueFromBuffer(value, type)
        else:
            self.__value, self.__valueLen = GetStringValueFromBuffer(value)

    def GetName(self):
        return self.__name

    def GetValue(self):
        return self.__value
    
    def GetBinaryValue(self) -> bytearray: 
        if (IsNumericalTypeValue(self.__type)):
            return struct.pack(PACK_TAB[self.__type], self.__value)
        
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
        #if (IsNumericalTypeValue(self.__type)):
        #    if value == '':
        #        value = 0
        #    self.__value = float(value)

        if (IsIntegerTypeValue(self.__type)):
            if value == '':
                value = 0
            self.__value = int(value)
        
        elif (IsFloatTypeValue(self.__type)):
            if value == '':
                value = 0.0
            self.__value = float(value)

        elif (IsBoolTypeValue(self.__type)):
            if value == '' or value == '0':
                value = False
            self.__value = bool(value)
            

    def SetBinaryValue(self, value:bytearray):
        if (IsNumericalTypeValue(self.__type)):
            self.__value = (struct.unpack(PACK_TAB[self.__type], value)[0])

        elif (IsUInt32TypeValue(self.__type)):
            self.__value = struct.unpack('<I', value)[0]

    def AppendValueToBuffer(self, buffer:bytearray):
        value = self.GetBinaryValue()

        buffer.append(value.__len__())

        for i in range(0, value.__len__()):
            buffer.append(value[i])

