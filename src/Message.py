from Setting import *

def GetBytes(buffer:bytearray, index:int):
    arraySize = buffer[index]

    retArray = buffer[index+1:index+1+arraySize]

    return retArray

def GetString(buffer:bytearray, msgIndex:int):
    strBytes = GetBytes(buffer, msgIndex)

    string = str()

    strLen = strBytes.__len__()

    index = 0

    while(index != strLen):
        string += chr(strBytes[index])
        index += 1

    msgIndex += index
    return string

class MessageType(Enum):
    UNINITIALISED:int = 0x01
    SETTING_UPDATE:int = 0x11
    INIT_REQUEST:int = 0x12
    SETTING_INIT:int = 0x13
    NOTIF:int = 0x14
    CONFIG_ESP_NOW_DIRECT_NOTIF:int = 0x15
    CONFIG_ESP_NOW_DIRECT_SETTING_UPDATE:int = 0x16

    ESP_NOW_INIT_WITH_SSID:int = 0x54
    ESP_NOW_CONFIG_DIRECT_NOTF:int = 0x55
    ESP_NOW_CONFIG_DIRECT_SETTING_UPDATE:int = 0x56

class MessageControlFrame(Enum):
    START:int = 0xFF
    END:int = 0x00

def GetFrameMessage(buffer: bytearray) -> bytearray:
    size = buffer[2]
    size += buffer[1] << 8

    if (size == 0):
        return bytearray()
    
    if (buffer[0] != MessageControlFrame.START.value):
        return bytearray()
    
    if (buffer[size - 1] != MessageControlFrame.END.value):
        return bytearray()
    
    return buffer[0:size]

class Message():
    def __init__(self, buffer:bytearray=None) -> None:
        
        if buffer == None:
            self.__type = MessageType.UNINITIALISED.value
            self.__slaveID = 0
            self.__setting = None
            self.__buffer = None
        else:
            self.__type = buffer[4]
            self.__slaveID = buffer[3]
            self.__len = buffer.__len__()
            self.__buffer = buffer
            self.__setting = None

    def GetLength(self) -> int:
        return self.__len
    
    def GetType(self) -> int:
        return self.__type
    
    def GetSlaveID(self) -> int:
        return self.__slaveID
    
    def ExtractSettingUpdate(self) -> tuple:
        ref = 0
        newValue = bytearray()

        if self.GetType() == MessageType.SETTING_UPDATE.value:
            ref = self.__buffer[5]
            newValueLen = self.__buffer[6]
            newValue = self.__buffer[7:7+newValueLen]

        return (ref, newValue, self.GetSlaveID())

    def ExtractNotif(self) -> tuple:
        notifByte = 0
        slaveID = 0

        if self.GetType() == MessageType.NOTIF.value:
            notifByte = self.__buffer[5]
        
        return (notifByte, self.GetSlaveID())

    def GetSetting(self) -> Setting:
        return self.__setting
    
    def IsValid(self) -> bool:
        return self.__isValid

    def GetByteArray(self) -> bytearray:
        return self.__buffer

    def __CheckMsgSize(self, buffer:bytearray) -> bool:
        len = buffer.__len__()

        if (len < 7):
            return False

        if (buffer[0] != MessageControlFrame.START.value):
            return False

        if (buffer[len-1] != MessageControlFrame.END.value):
            return False

        size = buffer[2]
        size += buffer[1] << 8

        if (size != len):
            return False

        return True
        