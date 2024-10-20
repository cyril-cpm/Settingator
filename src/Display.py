from abc import ABC, abstractmethod
from typing import Type
from Setting import *

#enum display
IDP_BUTTON = 0x01
IDP_INPUT = 0x02
IDP_TEXT = 0x03
IDP_FRAME = 0x04
IDP_PLAYER_NAME_INPUT = 0x05

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
    def UpdateSetting(self,setting:Setting) -> None:
        pass