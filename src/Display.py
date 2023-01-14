from abc import ABC, abstractmethod
from typing import Type
from Setting import *

class IDisplay(ABC):
    def __init__(self, settingLayout:SettingLayout) -> None:
        self.__settingLayout = settingLayout

    @abstractmethod
    def DisplaySettings(self) -> None:
        pass

    @abstractmethod
    def Update(self) -> SettingList:
        pass