from abc import ABC, abstractmethod
from typing import Type

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

    def SetValue(self, value):
        self.__value = value

class SettingLayout():
    def __init__(self) -> None:
        self.__settingList = []

    @abstractmethod
    def Display(self) -> None:
        pass

    def AddSetting(self, setting:Setting) -> None:
        self.__settingList

    def SetSettingValue(self, ref, value) -> None:
        pass