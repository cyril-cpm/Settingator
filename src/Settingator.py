from Setting import *
from Communicator import ICTR
from Message import *
from Display import *
import queue
import threading

class Settingator:
    def __init__(self, ctr:ICTR, display:IDisplay) -> None:
        self.__communicator = ctr
        self.__slaveSettings = dict()
        self.__slaves = dict()
        self.__shouldUpdateDisplayLayout = False
        self.__shouldUpdateSetting = None
        self.__notifCallback = dict()
        self.__initCallback = dict()

        # Display Stuff
        self.__display = display
        self.__display.SetSlaveSettingsRef(self.__slaveSettings)
        self.__layout = LayoutElement(IDP_FRAME)
        self.__slaveLayout = LayoutElement(IDP_FRAME)
        self.__display.AddLayout(self.__layout)
        self.__display.AddLayout(self.__slaveLayout)

        self.__functionQueue = queue.Queue()

        return
    
    def PutFunctionToQueue(self, f, args):
        self.__functionQueue.put((f, args))

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
                        setting.SetBinaryValue(value)
                        self.__shouldUpdateSetting = setting

            elif msg.GetType() == MessageType.NOTIF.value:
                notifByte, slaveID = msg.ExtractNotif()

                if notifByte in self.__notifCallback:
                    self.__notifCallback[notifByte](slaveID)


            self.__communicator.Flush()

        self.__display.Update()
        
        while True:
            try:
                f, args = self.__functionQueue.get_nowait()
                f(*args)
            except queue.Empty:
                break

        if self.__shouldUpdateDisplayLayout:
            self.__display.UpdateLayout()
            self.__shouldUpdateDisplayLayout = False

        if self.__shouldUpdateSetting != None:
            self.__display.UpdateSetting(self.__shouldUpdateSetting)
            self.__shouldUpdateSetting = None

        return
    
    def SendBridgeInitRequest(self, slaveID:int, slaveName:bytearray, callbackFunction = None, expectedSlaveNumber:int = 1) -> None:
        
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

    def SendInitRequest(self, slaveID:int, callbackFunction = None) -> None:
        if callbackFunction != None:
            self.__initCallback[slaveID] = callbackFunction

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

        if not slaveID in self.__slaves:
            self.__slaves[slaveID] = Slave(self, slaveID, self.__slaveSettings[slaveID])

            slaveLayout = LayoutElement(IDP_COLUMN, None, "Slave "+str(slaveID))

            for settingRef in self.__slaveSettings[slaveID]:
                setting:Setting = self.__slaveSettings[slaveID][settingRef]
                settingType = setting.GetType()

                layoutElement:LayoutElement
                if settingType == SettingType.SLIDER.value:
                    layoutElement = LayoutElement(IDP_SLIDER, setting.GetName())
                    slaveLayout.AppendElement(layoutElement)
                
                elif settingType == SettingType.TRIGGER.value:
                    layoutElement = LayoutElement(IDP_BUTTON, setting.GetValue(), setting.GetName())
                    slaveLayout.AppendElement(layoutElement)

                elif settingType == SettingType.SWITCH.value or \
                    settingType == SettingType.BOOL.value:
                    layoutElement = LayoutElement(IDP_CHECK, setting.GetValue(), setting.GetName(), callback=lambda value, setting=setting : self.SendUpdateSetting(setting, value))
                    slaveLayout.AppendElement(layoutElement)

                elif settingType == SettingType.FLOAT.value or\
                    settingType == SettingType.UINT8.value or \
                    settingType == SettingType.UINT16.value or \
                    settingType == SettingType.UINT32.value or \
                    settingType == SettingType.CUSTOM_FLOAT.value:
                    slaveLayout.AppendElement(LayoutElement(IDP_TEXT, setting.GetName(), setting.GetName()))

                    layoutElement = LayoutElement(IDP_INPUT, setting.GetValue(), setting.GetName(), callback=lambda value, setting=setting : self.SendUpdateSetting(setting, value))
                    slaveLayout.AppendElement(layoutElement)

                else:
                    layoutElement = LayoutElement(IDP_TEXT, "Unhandled type : " + str(settingType))
                    slaveLayout.AppendElement(layoutElement)

                setting.SetLayoutElement(layoutElement)
                

            self.__slaveLayout.AppendElement(slaveLayout)
            self.__display.UpdateLayout()

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

    def SendUpdateSetting(self, setting:Setting, value = None) -> None:
        if threading.current_thread().name != "MainThread":
            self.PutFunctionToQueue(self.SendUpdateSetting, (setting, value))
            return
        
        if setting != None:
            if value != None:
                setting.SetValue(value)

            type = MessageType.SETTING_UPDATE.value
            buffer = bytearray()
            buffer.append(MessageControlFrame.START.value)
            buffer.append(0x00)
            buffer.append(0x00)
            buffer.append(setting.GetSlaveID())
            buffer.append(type)
            buffer.append(setting.GetRef())

            setting.AppendValueToBuffer(buffer)
            
            buffer.append(MessageControlFrame.END.value)
            size = buffer.__len__()
            buffer[1] = size >> 8
            buffer[2] = size

            self.__communicator.Write(Message(buffer))

    def GetSlaveSettings(self) -> dict:
        return self.__slaveSettings
    
    def AddNotifCallback(self, notifByte:int, callback) -> None:
        self.__notifCallback[notifByte] = callback

    def RemoveNotifCallback(self, notifByte:int) -> None:
        None
        
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

    def AddToLayout(self, layoutElement:LayoutElement) -> None:
        self.__layout.AppendElement(layoutElement)

    def RemoveFromLayout(self, layoutElement:LayoutElement) -> None:
        self.__layout.RemoveElement(layoutElement)

class Slave:
    def __init__(self, str:Settingator, slaveID:int, settings:dict) -> None:
        self.__ID = slaveID
        self.__settings = settings
        self.__str = str

    def GetSettingByRef(self, ref:int) -> Setting:
        return self.__settings[ref]

    def GetSettingByName(self, settingName:str) -> Setting:
        for setting in self.__settings:
            if self.__settings[setting].GetName() == settingName:
                return self.GetSettingByRef(setting)
        return None

    def SendSettingUpdateByRef(self, ref:int, value = None):
        self.__str.SendUpdateSetting(self.__settings[ref], value)

    def SendSettingUpdateByName(self, settingName:str, value = None):

        for setting in self.__settings:
            if self.__settings[setting].GetName() == settingName:
                self.SendSettingUpdateByRef(self.__settings[setting].GetRef(), value)
                break

    def ConfigDiretNotif(self, target, notifByte:int):
        self.__str.ConfigDirectNotf(self.__ID, target.GetID(), notifByte)

    def ConfigDirectSettingUpdate(self, target, settingRef:int):
        self.__str.ConfigDirectSettingUpdate(self.__ID, target.GetID(), settingRef)

    def RemoveDirectSettingUpdateConfig(self, target, settingRef:int):
        self.__str.RemoveDirectSettingUpdateConfig(self.__ID, target.GetID(), settingRef)

    def GetID(self):
        return self.__ID