from Setting import *
from TestCommunicator import *
from PySimpleGUIDisplay import *
from PySerialCommunicator import *

#GetPortList()

#communicator = TCommunicator()
#communicator.SendInitRequest()
#settingLayout = communicator.GetSettingLayout()

mySerial = PySerial("COM4")

communicator = Communicator(mySerial)

communicator.SendInitRequest(0)

settingLayout = None
while (settingLayout == None):
    settingLayout = communicator.GetSettingLayout()


displayer = PySimpleGUIDisplay(settingLayout)

displayer.DisplaySettings()

while (True):
    communicator.SendSettingsUpdate(displayer.Update())
