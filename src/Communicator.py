from abc import ABC, abstractmethod
from typing import Type
from Setting import *
from Message import *

class ICommunicator(ABC):
    def __init__(self) -> None:
        pass

    def SendInitRequest(self,param:int) -> None:
        pass
    
    def GetSettingLayout(self) -> Type[SettingLayout]:
        pass

    def SendSettingsUpdate(self, settingList: SettingList) -> None:
        size = settingList.GetSize()

        i = 0
        while (i != size):
            self.__SendSettingUpdate(settingList.GetSetting(i))
            i += 1

    def __SendSettingUpdate(self, setting:Setting) -> None:
        message = Message(setting)