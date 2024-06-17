from Setting import *
from Communicator import ICTR
from Message import *
from Display import *

class Settingator:
    def __init__(self, ctr:ICTR, display:IDisplay) -> None:
        self.__communicator = ctr
        self.__display = display
        self.__slaveSettings = dict()
        self.__display.SetSlaveSettingsRef(self.__slaveSettings)
        self.__shouldUpdateDisplayLayout = False
        self.__shouldUpdateSetting = None
        self.__notifCallback = dict()
        return
    
    def Update(self) -> None:

        if self.__communicator.Available():

            msg:Message = self.__communicator.Read()

            if msg.GetType() == MessageType.SETTING_INIT.value:
                self.__ParseSettingInit(msg.GetByteArray())

            elif msg.GetType() == MessageType.SETTING_UPDATE.value:
                ref, value, slaveID = msg.ExtractSettingUpdate()
                setting = self.__slaveSettings[slaveID][ref]
                setting.SetValue(value)
                self.__shouldUpdateSetting = (slaveID, ref)

            elif msg.GetType() == MessageType.NOTIF.value:
                notifByte, slaveID = msg.ExtractNotif()

                if notifByte in self.__notifCallback:
                    self.__notifCallback[notifByte](slaveID)


            self.__communicator.Flush()

        self.SendUpdateSetting(self.__display.Update())
        
        if self.__shouldUpdateDisplayLayout:
            self.__display.UpdateLayout(self.__slaveSettings)
            self.__shouldUpdateDisplayLayout = False

        if self.__shouldUpdateSetting != None:
            self.__display.UpdateSetting(self.__shouldUpdateSetting)
            self.__shouldUpdateSetting = None

        return
    
    def SendBridgeInitRequest(self, slaveID:int, slaveName:bytearray) -> None:
        type = MessageType.ESP_NOW_INIT_WITH_SSID.value
        byteArray = bytearray()
        byteArray.append(MessageControlFrame.START.value)
        byteArray.append(0x00)
        byteArray.append(0x00)
        byteArray.append(slaveID)
        byteArray.append(type)
        byteArray += slaveName
        byteArray.append(MessageControlFrame.END.value)
        size = byteArray.__len__()
        byteArray[1] = size >> 8
        byteArray[2] = size

        bridgeInitRequest = Message(byteArray)
        self.__communicator.Write(bridgeInitRequest)

    def __ParseSettingInit(self, byteArray:bytearray) -> bool:
        isValid = True

        slaveID = byteArray[3]
        if not slaveID in self.__slaveSettings:
            self.__slaveSettings[slaveID] = dict()
        
        nbSetting = byteArray[5]

        msgIndex = 6
        loopIndex = 0

        while((loopIndex < nbSetting) and isValid):
            msgIndex = self.__ParseSetting(byteArray, msgIndex, slaveID)
            if (msgIndex < 0):
                isValid = False

            loopIndex += 1

        if (loopIndex != nbSetting):
            isValid = False

        if (msgIndex != (byteArray.__len__() - 1) and byteArray[msgIndex] != MessageControlFrame.END.value):
            isValid = False
        
        self.__shouldUpdateDisplayLayout = True
        return isValid

    def __ParseSetting(self, byteArray:bytearray, msgIndex:int, slaveID:int) -> int:
        msgSize = byteArray.__len__()

        if (msgIndex >= msgSize):
            return -1

        ref = byteArray[msgIndex]

        msgIndex += 1
        if (msgIndex >= msgSize):
            return -1

        settingType = byteArray[msgIndex]
        
        msgIndex += 1  
        if (msgIndex >= msgSize):
            return -1

        valueLen = byteArray[msgIndex]
        value = GetBytes(byteArray, msgIndex)

        msgIndex += valueLen + 1
        
        if (msgIndex >= msgSize):
            return -1

        nameLen = byteArray[msgIndex]

        if ((msgIndex + nameLen) >= msgSize):
            return -1

        name = GetString(byteArray, msgIndex)

        self.__slaveSettings[slaveID][ref] = Setting(ref, slaveID, name, settingType, value)
        
        msgIndex += nameLen + 1

        return msgIndex

    def SendUpdateSetting(self, setting:Setting) -> None:
        if setting != None:
            type = MessageType.SETTING_UPDATE.value
            byteArray = bytearray()
            byteArray = bytearray()
            byteArray.append(MessageControlFrame.START.value)
            byteArray.append(0x00)
            byteArray.append(0x00)
            byteArray.append(setting.GetSlaveID())
            byteArray.append(type)
            byteArray.append(setting.GetRef())
            byteArray.append(0x01)
            byteArray.append(setting.GetValue())
            byteArray.append(MessageControlFrame.END.value)
            size = byteArray.__len__()
            byteArray[1] = size >> 8
            byteArray[2] = size

            self.__communicator.Write(Message(byteArray))

    def GetSlaveSettings(self) -> dict:
        return self.__slaveSettings
    
    def AddNotifCallback(self, notifByte:int, callback) -> None:
        self.__notifCallback[notifByte] = callback