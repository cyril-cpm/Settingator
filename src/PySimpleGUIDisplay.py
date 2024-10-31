from Display import *
from Setting import *
import PySimpleGUI as sg

class PySimpleGUIDisplay(IDisplay):
    def __init__(self) -> None:
        IDisplay.__init__(self)

        self.__PSGLayout = [[]]
        self.__PreLayout = []
        
        self.__PSGWindow = sg.Window('Settingator', self.__PSGLayout, element_justification='left', finalize=True)

    def GetPSGLayout(self):
        return self.__PSGLayout

    def AddPreLayout(self, element:tuple) -> None:
        self.__PreLayout.append(element)

    def RemovePreLayout(self, element:tuple) -> None:
        self.__PreLayout.remove(element)

    def UpdateLayout(self, slaveSettings:dict = None) -> None:
        self.__PSGLayout = [[],[]]

        topFrameLayout = [[]]

        for element in self.__PreLayout:
            type, name, key = element
            if type == IDP_BUTTON:
                topFrameLayout[0].append(sg.Button(name, key=key))
            elif type == IDP_INPUT:
                topFrameLayout[0].append(sg.Input(name, key=key))
            elif type == IDP_TEXT:
                topFrameLayout[0].append(sg.Text(name, key=key))
            elif type == IDP_FRAME:
                frameLayout = [[]]
                for frameElement in key:
                    frameElementType, frameElementName, frameElementKey = frameElement
                    if frameElementType == IDP_BUTTON:
                        frameLayout[0].append(sg.Button(frameElementName, key=frameElementKey))
                    elif frameElementType == IDP_PLAYER_NAME_INPUT:
                        frameLayout[0].append(sg.Input(frameElementName.GetName(), key=frameElementKey, enable_events=True, size=10))

                topFrameLayout[0].append(sg.Frame(name, frameLayout))
        
        self.__PSGLayout[0].append(sg.Frame(title="", border_width=0, layout=topFrameLayout, vertical_alignment="top", expand_x=True, expand_y=True))

        bottomFrameLayout = [[]]
        slaveCtrlLayout = []
        
        if slaveSettings != None:
            slaveIndex = 0

            for slaveID in slaveSettings:
                slaveCtrlLayout.append([])
                slaveFrameLayout = [[]]

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
                    
                    slaveFrameLayout[0].append(element)
                
                slaveCtrlLayout[slaveIndex].append(sg.Frame("SlaveID: " + str(slaveID), slaveFrameLayout, vertical_alignment="bottom", expand_x=True))

                slaveIndex += 1
            
        bottomFrameLayout[0].append(sg.Output(expand_x=True, expand_y=True))
        bottomFrameLayout[0].append(sg.Column(slaveCtrlLayout, vertical_alignment="bottom"))

        self.__PSGLayout[1].append(sg.Frame(title="", border_width=0, layout=bottomFrameLayout, expand_x=True, expand_y=True))

        window = sg.Window('Settingator', self.__PSGLayout, element_justification='left', finalize=True)
        window.Maximize()
        self.__PSGWindow.close()
        self.__PSGWindow = window
        print(self.__PSGLayout)

    def UpdateSetting(self, setting:Setting) -> None:
        slaveID = setting.GetSlaveID()
        ref = setting.GetRef()

        if setting.GetType() == SettingType.LABEL.value:
            self.__PSGWindow.Element((slaveID, ref)).update(setting.GetName() + " : " + setting.GetValue())
        else:    
            self.__PSGWindow.Element((slaveID, ref)).update(setting.GetValue())

    def Update(self) -> Setting:
        event, values = self.__PSGWindow.read(0)
        setting:Setting = None
        if event != sg.TIMEOUT_KEY:
            if (event == sg.WIN_CLOSED):
                quit()

            if isinstance(event, tuple):
                slaveID, ref = event
                setting = self.GetSlaveSettings()[slaveID][ref]

                if (setting.GetType() != SettingType.TRIGGER.value):
                    setting.SetValue(int(values[event]))

            if callable(event):
                if event in values:
                    event(values[event])
                else:
                    event(self.__PSGWindow)
        return setting