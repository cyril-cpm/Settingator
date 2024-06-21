from Settingator import *
from PySerialCommunicator import *
from PySimpleGUIDisplay import *

com = SerialCTR("COM8")

display = PySimpleGUIDisplay()

def configFunction():
    STR.ConfigDirectSettingUpdate(4, 5, 1)


display.AddPreLayout(("Config", configFunction))

STR = Settingator(com, display)

def notifTest(slaveID:int):
    print("YoloLaNotif")
    print(slaveID)

def notifTestB(slaveID:int):
    print("YoloLaNotifB")
    print(slaveID)

def notifLaser(slaveID:int):
    #STR.SendUpdateSetting(STR.GetSlaveSettings()[5][1])
    print("Laser Detected")
    print(slaveID)

STR.AddNotifCallback(0x42, notifTest)
STR.AddNotifCallback(0x03, notifTestB)
STR.AddNotifCallback(0x69, notifLaser)

STR.SendBridgeInitRequest(4, b'Desk')
STR.SendBridgeInitRequest(5, b'Turret')

while True:
    STR.Update()
