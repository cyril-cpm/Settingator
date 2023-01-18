from Setting import *
from TestCommunicator import *
from PySimpleGUIDisplay import *
from PySerialCommunicator import *

GetPortList()

communicator = TCommunicator()

settingLayout = communicator.GetSettingLayout()

displayer = PySimpleGUIDisplay(settingLayout)

displayer.DisplaySettings()

communicator2 = PySerialCommunicator("COM3")

while (True):
    communicator2.SendSettingsUpdate(displayer.Update())
