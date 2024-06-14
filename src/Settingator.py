from Setting import *
from Communicator import ICTR
from Message import *

class Settingator:
    def __init__(self, ctr:ICTR) -> None:
        self.__communicator = ctr
        self.__slaveList = SlaveList()
        self.__shouldUpdateDisplay = False
        return
    
    def Update(self) -> None:

        if self.__communicator.Available():

            msg:Message = self.__communicator.Read()

            if msg.GetType() == MessageType.SETTING_INIT.value:
                self.__ParseSettingInit(msg.GetByteArray())

            self.__communicator.Flush()
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
        slave = self.__slaveList.AddSlave(slaveID)
        nbSetting = byteArray[5]

        msgIndex = 6
        loopIndex = 0

        while((loopIndex < nbSetting) and isValid):
            msgIndex = self.__ParseSetting(byteArray, msgIndex, slave)
            if (msgIndex < 0):
                isValid = False

            loopIndex += 1

        if (loopIndex != nbSetting):
            isValid = False

        if (msgIndex != (byteArray.__len__() - 1) and byteArray[msgIndex] != MessageControlFrame.END.value):
            isValid = False
        
        self.__shouldUpdateDisplay = True
        return isValid

    def __ParseSetting(self, byteArray:bytearray, msgIndex:int, slave:SlaveSettings) -> int:
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

        #self.__settingList.AddSetting(Setting(ref, self.__slaveID, name, settingType, value))
        slave.AddSetting(Setting(ref, slave.GetID(), name, settingType, value))
        msgIndex += nameLen + 1

        return msgIndex
    
    def ShouldUpdateDisplay(self) -> bool:
        return self.__shouldUpdateDisplay
    
    def ResetShouldUpdateDisplay(self) -> None:
        self.__shouldUpdateDisplay = False
    
    def GetSlaveList(self) -> SlaveList:
        return self.__slaveList
    
    def GetSettingBySlaveIDAndRef(self, IDRef:tuple) -> Setting:
        return self.__slaveList.GetSettingBySlaveIDAndRef(IDRef)