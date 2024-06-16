from abc import ABC, abstractmethod
from typing import Type
from Setting import *

class IDisplay(ABC):
    def __init__(self, slaveSetting:dict) -> None:
        self.__slaveSetting = slaveSetting

    @abstractmethod
    def DisplaySettings(self) -> None:
        pass

    @abstractmethod
    def Update(self):
        pass