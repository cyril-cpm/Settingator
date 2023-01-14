from Display import *
from Setting import *
import PySimpleGUI as sg

class PySimpleGUIDisplay(IDisplay):
    def __init__(self, settingLayout: SettingLayout) -> None:
        super().__init__(settingLayout)
        self.__PSGLayout = [[]]
        
        settingList = super().GetSettingLayout().GetSettingList()

        size = settingList.GetSize()
        i = 0

        while (i != size):
            setting = settingList.GetSetting(i)
            settingType = setting.GetType()
            element:sg.Element

            if (settingType == SettingType.SLIDER):
                element=sg.Slider()
            
            elif (settingType == SettingType.TRIGGER):
                element=sg.Button()

            elif (settingType == SettingType.SWITCH):
                element=sg.Checkbox()

            self.__PSGLayout.append([element])
            i += 1

    def DisplaySettings(self) -> None:
        self.__PSGWindow = sg.Window('Clotilde Mon Amoureuse', self.__PSGLayout)

    def Update(self) -> SettingList:
        event, values = self.__PSGWindow.read()
        return SettingList()