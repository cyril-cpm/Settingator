from abc import ABC, abstractmethod
from typing import Type
from Setting import *

class ICommunicator(ABC):
    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def GetSettingLayout(self) -> Type[SettingLayout]:
        pass

    @abstractmethod
    def SendSettingsUpdate(self, settingList:SettingList) -> None:
        pass