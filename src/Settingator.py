from Setting import *
from TestCommunicator import *
from PySimpleGUIDisplay import *
from PySerialCommunicator import *

GetPortList()

#communicator = TCommunicator()
#communicator.SendInitRequest()
#settingLayout = communicator.GetSettingLayout()


mySerial = PySerial("COM3")

communicator2 = Communicator(mySerial)

communicator2.SendInitRequest(0)
settingLayout = communicator2.GetSettingLayout()


displayer = PySimpleGUIDisplay(settingLayout)

displayer.DisplaySettings()

while (True):
    communicator2.SendSettingsUpdate(displayer.Update())
