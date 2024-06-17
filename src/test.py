from Settingator import *
from PySerialCommunicator import *
from PySimpleGUIDisplay import *

com = SerialCTR("COM3")

display = PySimpleGUIDisplay()


STR = Settingator(com, display)

def notifTest(slaveID:int):
    print("YoloLaNotif")
    print(slaveID)

def notifTestB(slaveID:int):
    print("YoloLaNotifB")
    print(slaveID)

STR.AddNotifCallback(0x42, notifTest)
STR.AddNotifCallback(0x03, notifTestB)

STR.SendBridgeInitRequest(4, b'Desk')
STR.SendBridgeInitRequest(5, b'Turret')

while True:
    STR.Update()
