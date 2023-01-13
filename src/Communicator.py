from abc import ABC, abstractmethod
from typing import Type
from Setting import *

class ICommunicator(ABC):
    @abstractmethod
    def GetSettingLayout(self) -> Type[SettingLayout]:
        pass

    @abstractmethod
    def SendSettingUpdate(self, setting:Setting) -> None:
        pass