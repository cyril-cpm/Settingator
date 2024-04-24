from Communicator import *
from Setting import *
import serial
import serial.tools.list_ports


def GetPortList():
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        print(port.device)

class PySerial(ISerial):
    def __init__(self, port:str) -> None:
        super().__init__()
        self.__port = port
        self.__serial = serial.Serial(port=port, baudrate=9600)
        self.__readBuffer = bytearray()
        self.__nextMessageFrame = None

    def read(self) -> bytearray:
        messageFrame = self.__nextMessageFrame
        self.__nextMessageFrame = None
        return messageFrame

    def write(self, data: bytearray) -> None:
        self.__serial.write(data)
        #print(data)

    def available(self) -> bool:
        self.__readBuffer.extend(self.__serial.read_all())

        startFrameIndex = self.__readBuffer.find(MessageControlFrame.START.value)
        if (startFrameIndex <= 0):
            self.__readBuffer = self.__readBuffer[startFrameIndex:]

        if (self.__readBuffer.__len__() >= 5):
            msgSize = (self.__readBuffer[1] << 8) + self.__readBuffer[2]

            if (self.__readBuffer.__len__() >= msgSize):
                if (self.__readBuffer[msgSize - 1] == MessageControlFrame.END.value):
                    self.__nextMessageFrame = self.__readBuffer[0: msgSize]
                    self.__readBuffer = self.__readBuffer[msgSize:]

        if (self.__nextMessageFrame != None):
            return True
        return False
