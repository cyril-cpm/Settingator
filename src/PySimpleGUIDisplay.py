from Display import *
from Setting import *
import PySimpleGUI as sg

class PySimpleGUIDisplay(IDisplay):
    def __init__(self, slaveSetting:dict) -> None:
        super().__init__(slaveSetting)
        self.__PSGLayout = [[]]
        self.__slaveSetting = slaveSetting
        
        self.__PSGWindow = sg.Window('Settingator', self.__PSGLayout, element_justification='c', finalize=True)

    def UpdateLayout(self, slaveSettings:dict) -> None:
        
        if slaveSettings != None:
            slaveIndex = 0
            self.__PSGLayout = []

            for slaveID in slaveSettings:
                self.__PSGLayout.append([])

                for ref in slaveSettings[slaveID]:
                    setting = slaveSettings[slaveID][ref]
                    settingType = setting.GetType()
                    element:sg.Element

                    if (settingType == SettingType.SLIDER.value):
                        element=sg.Column([[sg.Slider(range=(0,255), default_value=setting.GetValue(), key=(setting.GetSlaveID(), setting.GetRef()), change_submits=True)],
                                [sg.Text(setting.GetName())]])
                    
                    elif (settingType == SettingType.TRIGGER.value):
                        element=sg.Button(button_text=setting.GetName(), key=(setting.GetSlaveID(), setting.GetRef()))

                    elif (settingType == SettingType.SWITCH.value):
                        element=sg.Checkbox(text=setting.GetName(), key=(setting.GetSlaveID(), setting.GetRef()), change_submits=True)

                    elif (settingType == SettingType.LABEL.value):
                        element=sg.Text(setting.GetName() + " : " + setting.GetValue(), key=(setting.GetSlaveID(), setting.GetRef()))

                    else:
                        element=sg.Text("Not Supported Setting")
                    self.__PSGLayout[slaveIndex].append(element)

                slaveIndex += 1
            
            window = sg.Window('Settingator', self.__PSGLayout, element_justification='c', finalize=True)
            self.__PSGWindow.close()
            self.__PSGWindow = window
            print(self.__PSGLayout)

    def UpdateSetting(self, IDRef:tuple) -> None:
        slaveID, ref = IDRef
        setting = self.__slaveSetting[slaveID][ref]

        if setting.GetType() == SettingType.LABEL.value:
            self.__PSGWindow.Element(IDRef).update(setting.GetName() + " : " + setting.GetValue())
        else:    
            self.__PSGWindow.Element(IDRef).update(setting.GetValue())

    def DisplaySettings(self) -> None:
        pass

    def Update(self) -> Setting:
        event, values = self.__PSGWindow.read(0)
        setting:Setting = None
        if event != sg.TIMEOUT_KEY:
            if (event == sg.WIN_CLOSED):
                quit()

            slaveID, ref = event
            setting = self.__slaveSetting[slaveID][ref]

            if (setting.GetType() != SettingType.TRIGGER.value):
                setting.SetValue(int(values[event]))


        return setting