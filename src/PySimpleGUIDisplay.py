from Display import *
from Setting import *
import PySimpleGUI as sg

class PySimpleGUIDisplay(IDisplay):
    def __init__(self, slaveList:SlaveList = None) -> None:
        super().__init__(slaveList)
        self.__PSGLayout = [[]]
        self.__slaveList = slaveList
        
        if slaveList != None:
            slaveIndex = 0
            slaveNumber = slaveList.GetSize()
            while (slaveIndex != slaveNumber):
                slave = slaveList.GetSlave(slaveIndex)
                numberSetting = slave.GetNumberSetting()

                self.__PSGLayout.append([])

                i = 0
                while (i != numberSetting):
                    setting = slave.GetSetting(i)
                    settingType = setting.GetType()
                    element:sg.Element

                    if (settingType == SettingType.SLIDER.value):
                        element=sg.Column([[sg.Slider(range=(0,255), default_value=setting.GetValue(), key=setting.GetRef(), change_submits=True)],
                                [sg.Text(setting.GetName())]])
                    
                    elif (settingType == SettingType.TRIGGER.value):
                        element=sg.Button(button_text=setting.GetName(), key=setting.GetRef())

                    elif (settingType == SettingType.SWITCH.value):
                        element=sg.Checkbox(text=setting.GetName(), key=setting.GetRef(), change_submits=True)

                    #elif (settingType == SettingType.LABEL.value):
                    #   element=sg.Text(setting.GetName() + " : " + GetStringValue(setting.GetValue()))

                    else:
                        element=sg.Text("Not Supported Setting")
                    self.__PSGLayout[slaveIndex].append(element)
                    i += 1
                
                slaveIndex += 1

            print(self.__PSGLayout)
            self.__PSGWindow = sg.Window('Settingator', self.__PSGLayout, element_justification='c').finalize()
        else:
            self.__PSGWindow = sg.Window('Settingator', self.__PSGLayout, element_justification='c', finalize=True)

    def UpdateLayout(self, slaveList:SlaveList) -> None:
        
        if slaveList != None:
            self.__slaveList = slaveList

            slaveIndex = 0
            slaveNumber = slaveList.GetSize()

            self.__PSGLayout = []

            while (slaveIndex != slaveNumber):
                slave = slaveList.GetSlave(slaveIndex)
                numberSetting = slave.GetNumberSetting()

                self.__PSGLayout.append([])

                i = 0
                while (i != numberSetting):
                    setting = slave.GetSetting(i)
                    settingType = setting.GetType()
                    element:sg.Element

                    if (settingType == SettingType.SLIDER.value):
                        element=sg.Column([[sg.Slider(range=(0,255), default_value=setting.GetValue(), key=(setting.GetSlaveID(), setting.GetRef()), change_submits=True)],
                                [sg.Text(setting.GetName())]])
                    
                    elif (settingType == SettingType.TRIGGER.value):
                        element=sg.Button(button_text=setting.GetName(), key=(setting.GetSlaveID(), setting.GetRef()))

                    elif (settingType == SettingType.SWITCH.value):
                        element=sg.Checkbox(text=setting.GetName(), key=(setting.GetSlaveID(), setting.GetRef()), change_submits=True)

                    #elif (settingType == SettingType.LABEL.value):
                    #   element=sg.Text(setting.GetName() + " : " + GetStringValue(setting.GetValue()))

                    else:
                        element=sg.Text("Not Supported Setting")
                    self.__PSGLayout[slaveIndex].append(element)
                    i += 1
                

                slaveIndex += 1
            
            window = sg.Window('Settingator', self.__PSGLayout, element_justification='c', finalize=True)
            self.__PSGWindow.close()
            self.__PSGWindow = window
            print(self.__PSGLayout)
            
    def DisplaySettings(self) -> None:
        pass

    def Update(self) -> SettingList:
        event, values = self.__PSGWindow.read(0)
        settingList = SettingList()
        if event != sg.TIMEOUT_KEY:
            if (event == sg.WIN_CLOSED):
                quit()

            setting = self.__slaveList.GetSettingBySlaveIDAndRef(event)

            if (setting.GetType() != SettingType.TRIGGER.value):
                setting.SetValue(int(values[event]))

            settingList.AddSetting(setting)

        return settingList