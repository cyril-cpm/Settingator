from Setting import *
from Communicator import ICTR
from Message import *
from Display import *

class Settingator:
    def __init__(self, ctr:ICTR, display:IDisplay) -> None:
        self.__communicator = ctr
        self.__display = display
        self.__slaveSettings = dict()
        self.__slaves = dict()
        self.__display.SetSlaveSettingsRef(self.__slaveSettings)
        self.__shouldUpdateDisplayLayout = False
        self.__shouldUpdateSetting = None
        self.__notifCallback = dict()
        self.__initCallback = dict()
        return
    
    def Update(self) -> None:

        if self.__communicator.Available():

            msg:Message = self.__communicator.Read()

            if msg.GetType() == MessageType.SETTING_INIT.value:
                self.__ParseSettingInit(msg.GetByteArray())

            elif msg.GetType() == MessageType.SETTING_UPDATE.value:
                ref, value, slaveID = msg.ExtractSettingUpdate()

                if slaveID in self.__slaveSettings:
                    if ref in self.__slaveSettings[slaveID]:
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
    
    def SendBridgeInitRequest(self, slaveID:int, slaveName:bytearray, callbackFunction:function = None, expectedSlaveNumber:int = 1) -> None:
        
        if callbackFunction != None:
            while expectedSlaveNumber != 0: 
                self.__initCallback[slaveID + expectedSlaveNumber - 1] = callbackFunction
                expectedSlaveNumber -= 1
        
        type = MessageType.ESP_NOW_INIT_WITH_SSID.value
        buffer = bytearray()
        buffer.append(MessageControlFrame.START.value)
        buffer.append(0x00)
        buffer.append(0x00)
        buffer.append(slaveID)
        buffer.append(type)
        buffer += slaveName
        buffer.append(MessageControlFrame.END.value)
        size = buffer.__len__()
        buffer[1] = size >> 8
        buffer[2] = size

        bridgeInitRequest = Message(buffer)
        self.__communicator.Write(bridgeInitRequest)

    def SendInitRequest(self, slaveID:int) -> None:
        type = MessageType.INIT_REQUEST.value
        buffer = bytearray()
        buffer.append(MessageControlFrame.START.value)
        buffer.append(0x00)
        buffer.append(0x07)
        buffer.append(slaveID)
        buffer.append(MessageType.INIT_REQUEST.value)
        buffer.append(0x00)
        buffer.append(MessageControlFrame.END.value)

        initRequest = Message(buffer)
        self.__communicator.Write(initRequest)

    def __ParseSettingInit(self, buffer:bytearray) -> bool:
        isValid = True

        slaveID = buffer[3]
        if not slaveID in self.__slaveSettings:
            self.__slaveSettings[slaveID] = dict()
            self.__slaves[slaveID] = Slave(slaveID, self.__slaveSettings[slaveID])
        
        nbSetting = buffer[5]

        msgIndex = 6
        loopIndex = 0

        while((loopIndex < nbSetting) and isValid):
            msgIndex = self.__ParseSetting(buffer, msgIndex, slaveID)
            if (msgIndex < 0):
                isValid = False

            loopIndex += 1

        if (loopIndex != nbSetting):
            isValid = False

        if (msgIndex != (buffer.__len__() - 1) and buffer[msgIndex] != MessageControlFrame.END.value):
            isValid = False
        
        self.__shouldUpdateDisplayLayout = True

        if slaveID in self.__initCallback:
            self.__initCallback[slaveID](self.__slaves[slaveID])

        return isValid

    def __ParseSetting(self, buffer:bytearray, msgIndex:int, slaveID:int) -> int:
        msgSize = buffer.__len__()

        if (msgIndex >= msgSize):
            return -1

        ref = buffer[msgIndex]

        msgIndex += 1
        if (msgIndex >= msgSize):
            return -1

        settingType = buffer[msgIndex]
        
        msgIndex += 1  
        if (msgIndex >= msgSize):
            return -1

        valueLen = buffer[msgIndex]
        value = GetBytes(buffer, msgIndex)

        msgIndex += valueLen + 1
        
        if (msgIndex >= msgSize):
            return -1

        nameLen = buffer[msgIndex]

        if ((msgIndex + nameLen) >= msgSize):
            return -1

        name = GetString(buffer, msgIndex)

        self.__slaveSettings[slaveID][ref] = Setting(ref, slaveID, name, settingType, value)
        
        msgIndex += nameLen + 1

        return msgIndex

    def SendUpdateSetting(self, setting:Setting) -> None:
        if setting != None:
            type = MessageType.SETTING_UPDATE.value
            buffer = bytearray()
            buffer.append(MessageControlFrame.START.value)
            buffer.append(0x00)
            buffer.append(0x00)
            buffer.append(setting.GetSlaveID())
            buffer.append(type)
            buffer.append(setting.GetRef())
            buffer.append(0x01)
            buffer.append(setting.GetValue())
            buffer.append(MessageControlFrame.END.value)
            size = buffer.__len__()
            buffer[1] = size >> 8
            buffer[2] = size

            self.__communicator.Write(Message(buffer))

    def GetSlaveSettings(self) -> dict:
        return self.__slaveSettings
    
    def AddNotifCallback(self, notifByte:int, callback) -> None:
        self.__notifCallback[notifByte] = callback

    def ConfigDirectNotf(self, srcSlaveID:int, dstSlaveID:int, notifByte:int) -> None:
        buffer = bytearray()
        buffer.append(MessageControlFrame.START.value)
        buffer.append(0x00)
        buffer.append(0x08)
        buffer.append(srcSlaveID)
        buffer.append(MessageType.ESP_NOW_CONFIG_DIRECT_NOTF.value)
        buffer.append(dstSlaveID)
        buffer.append(notifByte)
        buffer.append(MessageControlFrame.END.value)

        self.__communicator.Write(Message(buffer))

    def ConfigDirectSettingUpdate(self, srcSlaveID:int, dstSlaveID:int, settingRef) -> None:
        setting:Setting = None

        if dstSlaveID in self.__slaveSettings:
            if settingRef in self.__slaveSettings[dstSlaveID]:
                setting = self.__slaveSettings[dstSlaveID][settingRef]
            
            else:
                print("SettingRef " + str(settingRef) + " not found on Slave " + str(dstSlaveID))
        
        else:
            print("Slave " + str(dstSlaveID) + " not found")

        if setting != None:
            buffer = bytearray()
            buffer.append(MessageControlFrame.START.value)
            buffer.append(0x00)
            buffer.append(0x08)
            buffer.append(srcSlaveID)
            buffer.append(MessageType.ESP_NOW_CONFIG_DIRECT_SETTING_UPDATE.value)
            buffer.append(dstSlaveID)
            buffer.append(settingRef)
            buffer.append(setting.GetValueLen())
            buffer.append(MessageControlFrame.END.value)

            self.__communicator.Write(Message(buffer))

    def RemoveDirectMessageConfig(self, srcSlaveID:int, dstSlaveID:int, configID:int, configType:int) -> None:
        buffer = bytearray()
        buffer.append(MessageControlFrame.START.value)
        buffer.append(0x00)
        buffer.append(0x08)
        buffer.append(srcSlaveID)
        buffer.append(configType)
        buffer.append(dstSlaveID)
        buffer.append(configID)
        buffer.append(MessageControlFrame.END.value)

        self.__communicator.Write(Message(buffer))

    def RemoveDirectNotifConfig(self, srcSlaveID:int, dstSlaveID:int, notifByte:int) -> None:
        self.RemoveDirectMessageConfig(srcSlaveID, dstSlaveID, notifByte, MessageType.ESP_NOW_REMOVE_DIRECT_NOTIF_CONFIG.value)

    def RemoveDirectSettingUpdateConfig(self, srcSlaveID:int, dstSlave:int, settingRef:int) -> None:
        self.RemoveDirectMessageConfig(srcSlaveID, dstSlave, settingRef, MessageType.ESP_NOW_REMOVE_DIRECT_SETTING_UPDATE_CONFIG.value)



class Slave:
    def __init__(self, str:Settingator, slaveID:int, settings:dict) -> None:
        self.__ID = slaveID
        self.__settings = settings
        self.__str = str

    def SendSettingUpdateByRef(self, ref:int, value = None):

        if (value != None):
            self.__settings[ref].SetValue(value)

        self.__str.SendUpdateSetting(self, self.__settings[ref])

    def SendSettingUpdateByName(self, settingName:str, value = None):

        for setting in self.__settings:
            if setting.GetName() == settingName:
                self.SendSettingUpdateByRef(setting.GetRef(), value)
                break

    def ConfigDiretNotif(self, target, notifByte:int):
        self.__str.ConfigDirectNotf(self.__ID, target.GetID(), notifByte)

    def ConfigDirectSettingUpdate(self, target, settingRef:int):
        self.__str.ConfigDirectSettingUpdate(self.__ID, target.GetID(), settingRef)