from Communicator import *
from Setting import *
import serial
import serial.tools.list_ports


def GetCOMPortList() -> list:
    ports = list(serial.tools.list_ports.comports())
    portList = []
    for port in ports:
        portList.append(port.device)

    return portList

class PySerial(ISerial):
    def __init__(self, port:str) -> None:
        super().__init__()
        self.__port = port
        self.__serial:serial.Serial = serial.Serial()
        self.__serial.port=port
        self.__serial.baudrate=115200
        self.__serial.setDTR(False)
        self.__serial.setRTS(False)
        self.__serial.open()
        
        self.__readBuffer = bytearray()

    def read(self) -> bytearray:
        ret = self.__readBuffer
        self.__readBuffer = bytearray()
        return ret

    def write(self, data: bytearray) -> None:
        self.__serial.write(data)
        print("->")
        print(data)

    def available(self) -> int:
        self.__readBuffer = self.__serial.read_all()
        
        if (self.__readBuffer.__len__() > 0):
            print("<-")
            print(self.__readBuffer)

        return self.__readBuffer.__len__()

class SerialCTR(ICTR):
    def __init__(self, port:str="NULL") -> None:
        super().__init__()
        self.__port = port
        self.__serialBuffer = bytearray()
        self.__serialBufferSize = 0
        self.__serial = PySerial(port)

    def Write(self, message:Message) -> int:
        self.__serial.write(message.GetByteArray())
        return 0
    
    def Update(self) -> None:
        n:int = 0

        n = self.__serial.available()

        if n:
            self.__serialBuffer.extend(self.__serial.read())
            self.__serialBufferSize = self.__serialBuffer.__len__()
        
        startFrameIndex = self.__serialBuffer.find(MessageControlFrame.START.value)
        
        if (startFrameIndex >= 0):
            self.__serialBuffer = self.__serialBuffer[startFrameIndex:]

            if (self.__serialBuffer.__len__() >= 5):
                msgSize = (self.__serialBuffer[1] << 8) + self.__serialBuffer[2]

                if (self.__serialBuffer.__len__() >= msgSize):
                    if (self.__serialBuffer[msgSize - 1] == MessageControlFrame.END.value):
                        self._receive(Message(self.__serialBuffer[:msgSize]))
                        self.__serialBuffer = self.__serialBuffer[msgSize:]
        return
    
    def GetCOMPortList() -> list:
        return GetCOMPortList()
    