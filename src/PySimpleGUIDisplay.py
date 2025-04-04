from Display import *
from Setting import *
import PySimpleGUI as sg
import sys

class IRefreshable(ABC):
    def RefreshElementDisplay(self) -> None:
        pass

class PySimpleGUIDisplay(IDisplay):
    def __init__(self) -> None:
        IDisplay.__init__(self)

        self.__PSGLayout = [[]]
        
        self.__PSGWindow = sg.Window('Settingator', self.__PSGLayout, element_justification='left', finalize=True)

        self.__elementToRefresh = []
        self.__stuffToClose = []
        self.__isRunning = True

    def IsRunning(self):
        return self.__isRunning

    def AddElementToRefresh(self, element) -> None:
        self.__elementToRefresh.append(element)

    def AddStuffToClose(self, stuffToClose) -> None:
        self.__stuffToClose.append(stuffToClose)

    def GetPSGLayout(self):
        return self.__PSGLayout

    def __UpdateLayout(self, layout, elementList, isColumn:bool = False):
        
        for element in elementList:
            type:int = element.GetType()
            name = element.GetName()
            
            if isinstance(name, Mutable):
                name = name.GetValue()

            key = element.GetKey()
            ret:Mutable = element.GetRet()

            newElement:sg.Element

            if type == IDP_BUTTON:
                newElement = sg.Button(name, key=key)

            elif type == IDP_INPUT:
                newElement = sg.Input(name, key=key, enable_events=True, size=10)

            elif type == IDP_TEXT:
                newElement = sg.Text(name, key=key)

            elif type == IDP_FRAME:
                frameLayout = [[]]
                
                self.__UpdateLayout(frameLayout, key)

                newElement = sg.Frame(name, frameLayout)

            elif type == IDP_COLUMN:
                columnLayout = [[]]

                self.__UpdateLayout(columnLayout, key, True)

                newElement = sg.Frame(name, columnLayout, border_width=0)

            if ret != None:
                ret.SetValue(newElement)

            if isColumn:
                layout.append([newElement])
            else:
                layout[0].append(newElement)

    def UpdateLayout(self, slaveSettings:dict = None) -> None:
        self.__PSGLayout = [[],[]]

        topFrameLayout = [[]]

        self.__UpdateLayout(topFrameLayout, self._Layout.GetKey())
        
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

                    elif (settingType == SettingType.CUSTOM_FLOAT.value):
                        element=sg.Column([[sg.Slider(range=(0.0, 180.0), default_value=setting.GetValue(), key=(setting.GetSlaveID(), setting.GetRef()), change_submits=True)],
                                            [sg.Input(str(setting.GetValue()), key=(setting.GetSlaveID(), setting.GetRef(), 'INPUT'), enable_events=True, size=10)],
                                            [sg.Text(setting.GetName())]])

                    elif (settingType == SettingType.UINT32.value):
                        element=sg.Column([[sg.Input(setting.GetValue(), key=(setting.GetSlaveID(), setting.GetRef()), enable_events=False, size=30)],
                                           [sg.Button(button_text="Validate", key=(setting.GetSlaveID(), setting.GetRef(), 'BUTTON'))]])

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

        for elementToRefresh in self.__elementToRefresh:
            elementToRefresh.RefreshElementDisplay()
        window.read(0)
        
    def UpdateSetting(self, setting:Setting) -> None:
        slaveID = setting.GetSlaveID()
        ref = setting.GetRef()

        if setting.GetType() == SettingType.LABEL.value:
            self.__PSGWindow.Element((slaveID, ref)).update(setting.GetName() + " : " + setting.GetValue())
        elif setting.GetType() == SettingType.CUSTOM_FLOAT.value:
            self.__PSGWindow.Element((slaveID, ref)).update(setting.GetValue())
            self.__PSGWindow.Element((slaveID, ref, 'INPUT')).update(setting.GetValue())
        else:    
            self.__PSGWindow.Element((slaveID, ref)).update(setting.GetValue())

    def Update(self) -> Setting:
        event, values = self.__PSGWindow.read(0)
        setting:Setting = None
        if event != sg.TIMEOUT_KEY:
            if (event == sg.WIN_CLOSED):
                for stuff in self.__stuffToClose:
                    stuff.Close()
                self.__isRunning = False

            if isinstance(event, tuple):
                slaveID, ref, *info = event
                setting = self.GetSlaveSettings()[slaveID][ref]

                if (setting.GetType() != SettingType.TRIGGER.value):

                    if info.__len__() and info[0] == 'BUTTON':
                        setting.SetValue(values[(slaveID, ref)])
                        self.UpdateSetting(setting)
                    else:
                        setting.SetValue(values[event])
                        

                    if info.__len__():
                        self.__PSGWindow.Element((slaveID, ref)).update(setting.GetValue())
                    else:
                        self.UpdateSetting(setting)

            if callable(event):
                if event in values:
                    event(values[event])
                else:
                    event(self.__PSGWindow)
        return setting
    
    def SelectCOMPort(serialCTR) -> str:
        portList = serialCTR.GetCOMPortList()

        combo = sg.Combo(portList, default_value=portList[portList.__len__()-1] if portList.__len__() > 0 else "", expand_x=True, key="COM")
        button = sg.Button("Sélectionner", key="select_button")

        layout = [
            [combo],
            [button]
            ]
        
        portSelectionWindow = sg.Window("COM port selection",  layout, finalize=True)

        selecting = True

        while selecting:
            event, values = portSelectionWindow.read(0)

            if event != sg.TIMEOUT_KEY:
                if event == "select_button":
                    portSelectionWindow.close()
                    return values["COM"]
                
    def Close(self) -> None:
        self.__PSGWindow.Close()
        self.__isRunning = False