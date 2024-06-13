from abc import ABC, abstractmethod
from typing import Type
from Setting import *
from Message import *
from collections import deque

class ISerial():
    def read(self) -> bytearray:
        pass

    def write(self, data:bytearray) -> None:
        pass

    def available(self) -> int:
        pass

class Communicator(ABC):
    def __init__(self, serial:ISerial) -> None:
        self.__serial = serial

    def SendInitRequest(self,param:int) -> None:
        initRequest = Message(MessageType.INIT_REQUEST.value)
        initRequest.SetInitRequest(param)
        self.__serial.write(initRequest.GetByteArray())
    
    

    def GetSettingLayout(self) -> Type[SettingLayout]:
        while (not(self.__serial.available())):
            pass

        message = Message(MessageType.SETTING_INIT.value)
        message.FromByteArray(self.__serial.read())

        if (message.IsValid()):
            layout =  SettingLayout()
            layout.SetSettingList(message.GetSettingList())
            return layout
        else:
            return None

    def SendSettingsUpdate(self, settingList: SettingList) -> None:
        size = settingList.GetSize()

        i = 0
        while (i != size):
            self.__SendSettingUpdate(settingList.GetSetting(i))
            i += 1
        self.__serial.available()

    def Available(self) -> bool:



        return False

    def Update(self) -> None:
        pass

    def __SendSettingUpdate(self, setting:Setting) -> None:

        message = Message(MessageType.SETTING_UPDATE.value)
        message.FromSetting(setting)
        self.__serial.write(message.GetByteArray())

class ICTR(ABC):
    def __init__(self) -> None:
        self.__receivedMessage = deque()

    def Available(self) -> bool:
        self.Update()
        return self.__receivedMessage.__len__()
    
    def Write(self, message:Message) -> int:
        pass

    def Read(self) -> Message:
        return self.__receivedMessage[0]
    
    def Flush(self) -> None:
        self.__receivedMessage.popleft()
        return
    
    def Update(self) -> None:
        pass

    def GetBoxSize(self) -> int:
        return self.__receivedMessage.__len__()
    
    def _receive(self, message:Message) -> None:
        self.__receivedMessage.append(message)
        
        print("**")
        print(message.GetByteArray())
        print("**")
        return