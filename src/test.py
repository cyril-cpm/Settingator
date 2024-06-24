from Settingator import *
from PySerialCommunicator import *
from PySimpleGUIDisplay import *

com = SerialCTR("COM8")

display = PySimpleGUIDisplay()


targetting = False
step = 0
speed_setting:Setting
target_side = ""
left_trigger:Setting
right_trigger:Setting

def targetRight(window:sg.Window):
    #STR.ConfigDirectSettingUpdate(4, 5, 2) #A améliorer
    
    global targetting
    global target_side
    global speed_setting
    global step
    global left_trigger
    global right_trigger

    targetting = True
    target_side = "R"
    step = 0

    speed_setting = STR.GetSlaveSettings()[5][0] #A améliorer
    speed_setting.SetValue(255)

    left_trigger = STR.GetSlaveSettings()[5][1]
    right_trigger = STR.GetSlaveSettings()[5][3]

    STR.SendUpdateSetting(speed_setting)
    STR.SendUpdateSetting(right_trigger)

    display.UpdateSetting((speed_setting.GetSlaveID(), speed_setting.GetRef()))


display.AddPreLayout((IDP_BUTTON, "targetRight", targetRight))

STR = Settingator(com, display)


def notifLaser(slaveID:int):

    global step
    global speed_setting
    global target_side
    global targetting
    global left_trigger
    global right_trigger

    if targetting:
        if step == 0:
            speed_setting.SetValue(192)
            STR.SendUpdateSetting(speed_setting)

            if target_side == "R":
                STR.SendUpdateSetting(left_trigger)
            elif target_side == "L":
                STR.SendUpdateSetting(left_trigger)
            step = 3

        elif step == 3:
            speed_setting.SetValue(128)
            STR.SendUpdateSetting(speed_setting)

            if target_side == "R":
                STR.SendUpdateSetting(right_trigger)
            elif target_side == "L":
                STR.SendUpdateSetting(left_trigger)
            step = 4

        elif step == 4:
            step = 0
            target_side = ""
            targetting = False
            #STR.RemoveDirectSettingUpdateConfig(4, 5, 2)
            STR.SendUpdateSetting(STR.GetSlaveSettings()[5][2])
            STR.SendUpdateSetting(STR.GetSlaveSettings()[5][4])
        
            


        display.UpdateSetting((speed_setting.GetSlaveID(), speed_setting.GetRef()))
    print("Laser Detected")
    print(slaveID)

STR.AddNotifCallback(0x05, notifLaser)

STR.SendBridgeInitRequest(4, b'Desk')
STR.SendBridgeInitRequest(5, b'Turret')

display.UpdateLayout(None)

while True:
    STR.Update()
