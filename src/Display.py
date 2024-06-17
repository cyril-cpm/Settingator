from abc import ABC, abstractmethod
from typing import Type
from Setting import *

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
    def UpdateSetting(self, IDRef:tuple) -> None:
        pass