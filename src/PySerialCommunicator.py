from Communicator import *
from Setting import *
import serial
import serial.tools.list_ports



def GetPortList():
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        print(port.device)

class PySerialCommunicator(ICommunicator):
    def __init__(self, port:str) -> None:
        super().__init__()
        self.__port = port
