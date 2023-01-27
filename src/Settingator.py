from Setting import *
from TestCommunicator import *
from PySimpleGUIDisplay import *
from PySerialCommunicator import *

GetPortList()

communicator = TCommunicator()
communicator.SendInitRequest()
settingLayout = communicator.GetSettingLayout()

displayer = PySimpleGUIDisplay(settingLayout)

displayer.DisplaySettings()

communicator2 = PySerialCommunicator("COM3")

while (True):
    communicator.SendSettingsUpdate(displayer.Update())
