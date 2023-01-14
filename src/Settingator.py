from Setting import *
from TestCommunicator import *
from PySimpleGUIDisplay import *

communicator = TCommunicator()

settingLayout = communicator.GetSettingLayout()

displayer = PySimpleGUIDisplay(settingLayout)

displayer.DisplaySettings()

while (True):
    displayer.Update()

communicator.SendSettingsUpdate(settingLayout.GetSettingList())