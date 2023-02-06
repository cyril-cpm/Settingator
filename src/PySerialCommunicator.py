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
        self.__serial = serial.Serial(port)
        self.__readBuffer = bytearray()

    def read(self) -> bytearray:
        self.__readBuffer.append(self.__serial.read_all())
        messageFrame = GetFrameMessage(self.__readBuffer)
        messageFrameSize = messageFrame.__len__()
        readBufferSize = self.__readBuffer.__len__()
        self.__readBuffer = self.__readBuffer[messageFrameSize-1:readBufferSize-1]
        return messageFrame

    def write(self, data: bytearray) -> None:
        self.__serial.write(data)

    def available(self) -> bool:
        self.__readBuffer.append(self.__serial.read_all())

        if (self.__byteArray.__len__() > 0):
            return True
        return False
