from Settingator import *
from PySerialCommunicator import *

com = SerialCTR("COM8")

STR = Settingator(com)

STR.SendBridgeInitRequest(4, b'Desk')
STR.SendBridgeInitRequest(5, b'Turret')

while True:
    STR.Update()
