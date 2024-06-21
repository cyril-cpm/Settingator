from Setting import *

def GetBytes(byteArray:bytearray, index:int):
    arraySize = byteArray[index]

    retArray = byteArray[index+1:index+1+arraySize]

    return retArray

def GetString(byteArray:bytearray, msgIndex:int):
    strBytes = GetBytes(byteArray, msgIndex)

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

def GetFrameMessage(byteArray: bytearray) -> bytearray:
    size = byteArray[2]
    size += byteArray[1] << 8

    if (size == 0):
        return bytearray()
    
    if (byteArray[0] != MessageControlFrame.START.value):
        return bytearray()
    
    if (byteArray[size - 1] != MessageControlFrame.END.value):
        return bytearray()
    
    return byteArray[0:size]

class Message():
    def __init__(self, buffer:bytearray=None) -> None:
        
        if buffer == None:
            self.__type = MessageType.UNINITIALISED.value
            self.__slaveID = 0
            self.__setting = None
            self.__byteArray = None
        else:
            self.__type = buffer[4]
            self.__slaveID = buffer[3]
            self.__len = buffer.__len__()
            self.__byteArray = buffer
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
            ref = self.__byteArray[5]
            newValueLen = self.__byteArray[6]
            newValue = self.__byteArray[7:7+newValueLen]

        return (ref, newValue, self.GetSlaveID())

    def ExtractNotif(self) -> tuple:
        notifByte = 0
        slaveID = 0

        if self.GetType() == MessageType.NOTIF.value:
            notifByte = self.__byteArray[5]
        
        return (notifByte, self.GetSlaveID())

    def GetSetting(self) -> Setting:
        return self.__setting
    
    def IsValid(self) -> bool:
        return self.__isValid

    def GetByteArray(self) -> bytearray:
        return self.__byteArray

    def __CheckMsgSize(self, byteArray:bytearray) -> bool:
        len = byteArray.__len__()

        if (len < 7):
            return False

        if (byteArray[0] != MessageControlFrame.START.value):
            return False

        if (byteArray[len-1] != MessageControlFrame.END.value):
            return False

        size = byteArray[2]
        size += byteArray[1] << 8

        if (size != len):
            return False

        return True
        