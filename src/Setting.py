from abc import ABC, abstractmethod
from typing import Type
from enum import Enum

class SettingType(Enum):
    SLIDER = 1
    TRIGGER = 2
    SWITCH = 3

class Setting():
    def __init__(self, ref:int, name:str, type:int, value:int = 0) -> None:
        self.__ref = ref
        self.__name = name
        self.__type = type
        self.__value = value

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

    def GetSize(self) -> int:
        return self.__settings.__len__()

class SettingLayout():
    def __init__(self) -> None:
        self.__settingList = SettingList()

    def AddSetting(self, setting:Setting) -> None:
        self.__settingList.AddSetting(setting)

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