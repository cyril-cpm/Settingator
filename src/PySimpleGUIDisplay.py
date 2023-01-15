from Display import *
from Setting import *
import PySimpleGUI as sg

class PySimpleGUIDisplay(IDisplay):
    def __init__(self, settingLayout: SettingLayout) -> None:
        super().__init__(settingLayout)
        self.__PSGLayout = [[],[]]
        
        settingList = super().GetSettingLayout().GetSettingList()

        size = settingList.GetSize()
        i = 0
        while (i != size):
            setting = settingList.GetSetting(i)
            settingType = setting.GetType()
            element:sg.Element

            if (settingType == SettingType.SLIDER):
                element=sg.Column([[sg.Slider(range=(0,255), default_value=setting.GetValue(), key=setting.GetRef(), change_submits=True)],
                        [sg.Text(setting.GetName())]])
            
            elif (settingType == SettingType.TRIGGER):
                element=sg.Button(button_text=setting.GetName(), key=setting.GetRef())

            elif (settingType == SettingType.SWITCH):
                element=sg.Checkbox(text=setting.GetName(), key=setting.GetRef(), change_submits=True)

            self.__PSGLayout[0].append(element)
            i += 1

        self.__PSGWindow = sg.Window('Clotilde Mon Amoureuse', self.__PSGLayout, element_justification='c').finalize()

    def DisplaySettings(self) -> None:
        pass

    def Update(self) -> SettingList:
        event, values = self.__PSGWindow.read()
        settingList = SettingList()

        if (event == sg.WIN_CLOSED):
            quit()

        setting = self.GetSettingLayout().GetSettingList().GetSetting(event)

        if (setting.GetType() != SettingType.TRIGGER):
            setting.SetValue(int(values[event]))

        settingList.AddSetting(setting)

        return settingList