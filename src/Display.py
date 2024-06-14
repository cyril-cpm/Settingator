from abc import ABC, abstractmethod
from typing import Type
from Setting import *

class IDisplay(ABC):
    def __init__(self, slaveList:SlaveList) -> None:
        self.__slaveList = slaveList

    def GetSettingLayout(self):
        return self.__slaveList

    @abstractmethod
    def DisplaySettings(self) -> None:
        pass

    @abstractmethod
    def Update(self) -> SettingList:
        pass