from Settingator import *
from PySerialCommunicator import *
from PySimpleGUIDisplay import *

com = SerialCTR("COM8")

STR = Settingator(com)

STR.SendBridgeInitRequest(4, b'Desk')
STR.SendBridgeInitRequest(5, b'Turret')

displayer = PySimpleGUIDisplay()

while True:
    STR.Update()

    if STR.ShouldUpdateDisplay() == True:
        #displayer = PySimpleGUIDisplay(STR.GetSlaveList())
        displayer.UpdateLayout(STR.GetSlaveList())
        STR.ResetShouldUpdateDisplay()

    
    displayer.Update()

