from Communicator import *

class TCommunicator(ICommunicator):
    def __init__(self) -> None:
        super().__init__()

    def GetSettingLayout(self) -> Type[SettingLayout]:
        layout = SettingLayout()
        layout.AddSetting(Setting(0, "Slider1", SettingType.SLIDER, 42))
        layout.AddSetting(Setting(0, "Trigger1", SettingType.TRIGGER))
        layout.AddSetting(Setting(0, "Switch1", SettingType.SWITCH, 0))
        return layout

    def SendSettingsUpdate(self, settingList: SettingList) -> None:
        size = settingList.GetSize()

        i = 0

        while(i != size):
            setting = settingList.GetSetting(i)
            print("SettingName  : ", setting.GetName())
            print("SettingValue : ", setting.GetValue())
            print("SettingType  : ", setting.GetType())
            print("SettingRef   : ", setting.GetRef())
            print("")
            i += 1

