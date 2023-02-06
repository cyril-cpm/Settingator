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
    SETTING_UPDATE:int = 0x11
    INIT_REQUEST:int = 0x12
    SETTING_INIT:int = 0x13

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
    
    return byteArray[0:size-1]

class Message():
    def __init__(self, type:int) -> None:
        self.__type = type

    def SetInitRequest(self, param:int) -> None:
        self.__type = MessageType.INIT_REQUEST.value
        self.__byteArray = bytearray()
        self.__byteArray.append(MessageControlFrame.START.value)
        self.__byteArray.append(0x00)
        self.__byteArray.append(0x00)
        self.__byteArray.append(self.__type)
        self.__byteArray.append(param)
        self.__byteArray.append(MessageControlFrame.END.value)
        size = self.__byteArray.__len__()
        self.__byteArray[1] = size >> 8
        self.__byteArray[2] = size
        self.__isValid = True

    def FromSetting(self, setting:Setting) -> None:
        self.__setting = setting
        self.__type = MessageType.SETTING_UPDATE.value
        self.__byteArray = bytearray()
        self.__byteArray.append(MessageControlFrame.START.value)
        self.__byteArray.append(0x00)
        self.__byteArray.append(0x00)
        self.__byteArray.append(self.__type)
        self.__byteArray.append(setting.GetRef())
        self.__byteArray.append(setting.GetValue())
        self.__byteArray.append(MessageControlFrame.END.value)
        size = self.__byteArray.__len__()
        self.__byteArray[1] = size >> 8
        self.__byteArray[2] = size
        self.__isValid = True


    def FromByteArray(self, byteArray:bytearray) -> None:
        self.__byteArray = byteArray
        self.__isValid = True

        self.__isValid = self.__CheckMsgSize(byteArray)
        if (not(self.__isValid)):
            return

        msgType = byteArray[3]
        if (msgType == MessageType.INIT_REQUEST.value):
            pass
        elif (msgType == MessageType.SETTING_INIT.value):
            self.__isValid = self.__ParseSettingInit(byteArray)
        elif (msgType == MessageType.SETTING_UPDATE.value):
            pass
        else:
            self.__isValid = False

    def GetSetting(self) -> Setting:
        return self.__setting

    def GetSettingList(self) -> SettingList:
        return self.__settingList

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
        
    def __ParseSettingInit(self, byteArray:bytearray) -> bool:
        isValid = True

        if (byteArray[3] != self.__type):
            isValid = False
            return isValid

        nbSetting = byteArray[4]

        self.__settingList = SettingList()

        msgIndex = 5
        loopIndex = 0

        while((loopIndex < nbSetting) and isValid):
            msgIndex = self.__ParseSetting(byteArray, msgIndex)
            if (msgIndex < 0):
                isValid = False

            loopIndex += 1

        if (loopIndex != nbSetting):
            isValid = False

        if (msgIndex != (byteArray.__len__() - 1) and byteArray[msgIndex] != MessageControlFrame.END.value):
            isValid = False
        
        self.__isValid = isValid

        return isValid

    def __ParseSetting(self, byteArray:bytearray, msgIndex:int) -> int:
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

        self.__settingList.AddSetting(Setting(ref, name, settingType, value))

        msgIndex += nameLen + 1

        return msgIndex

