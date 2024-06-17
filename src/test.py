from Settingator import *
from PySerialCommunicator import *
from PySimpleGUIDisplay import *

com = SerialCTR("COM3")

display = PySimpleGUIDisplay()


STR = Settingator(com, display)

STR.SendBridgeInitRequest(4, b'Desk')
STR.SendBridgeInitRequest(5, b'Turret')

while True:
    STR.Update()
