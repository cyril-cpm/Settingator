from Settingator import *
from PySerialCommunicator import *
from PySimpleGUIDisplay import *

com = SerialCTR("COM8")

STR = Settingator(com)

STR.SendBridgeInitRequest(4, b'Desk')
STR.SendBridgeInitRequest(5, b'Turret')

displayer = PySimpleGUIDisplay(STR.GetSlaveSettings())

while True:
    STR.Update()

    if STR.ShouldUpdateDisplayLayout() == True:
        displayer.UpdateLayout(STR.GetSlaveSettings()) #STR.GetSlaveList())
        STR.ResetShouldUpdateDisplayLayout()

    if STR.ShouldUpdateSetting():
        displayer.UpdateSetting(STR.GetSettingToUpdate())
        STR.ResetShouldUpdateSetting()

    
    STR.SendUpdateSetting(displayer.Update())

