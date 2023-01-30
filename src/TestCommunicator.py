from Communicator import *

class TCommunicator(ICommunicator):
    def __init__(self) -> None:
        super().__init__()

    def SendInitRequest(self) -> None:
        msg = Message(MessageType.INIT_REQUEST.value)

        msg.SetInitRequest(0)

        print(msg.GetByteArray())

    def GetSettingLayout(self) -> Type[SettingLayout]:
        layout = SettingLayout()
        #layout.AddSetting(Setting(0, "Slider1", SettingType.SLIDER, 42))
        #layout.AddSetting(Setting(1, "Trigger1", SettingType.TRIGGER))
        #layout.AddSetting(Setting(2, "Switch1", SettingType.SWITCH, 0))
        #layout.AddSetting(Setting(3, "Trigger2", SettingType.TRIGGER))
        
        #byteArray = bytearray([0xff, 0x00, 0x1D, 0x13, 0x02, 0x08, 0x01, 0x42, 0x0C, 0x55, 0x6E, 0x20, 0x53, 0x6C, 0x69, 0x64, 0x65, 0x72, 0x20, 0x42, 0x47, 0x67, 0x02, 0x87, 0x03, 0x2D, 0x5F, 0xB0, 0x00])
        byteArray = bytearray([0xff, 0x00, 0x1F, 0x13, 0x02, 0x08, 0x01, 0x01, 0x42, 0x0C, 0x55, 0x6E, 0x20, 0x53, 0x6C, 0x69, 0x64, 0x65, 0x72, 0x20, 0x42, 0x47, 0x67, 0x02, 0x01, 0x87, 0x03, 0x2D, 0x5F, 0xB0, 0x00])
        
        msg = Message(0)
        msg.FromByteArray(byteArray)
        
        print(msg.IsValid())
        if (msg.IsValid()):
            layout.SetSettingList(msg.GetSettingList())

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

