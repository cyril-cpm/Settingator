from Settingator import *
from PySerialCommunicator import *
from PySimpleGUIDisplay import *


com = SerialCTR("COM4")

display = PySimpleGUIDisplay()

STR = Settingator(com, display)

###   GAME SYSTEM    ###

GS_INIT = 0

gameStep = GS_INIT

class Player():
    def __init__(self):
        self.__score = 0
        self.__bonus = 0
        self.__fail = 0
        self.__slave = None
        self.__slaveID = -1

    def SetSlave(self, slave:Slave):
        self.__slave = slave

    def Send(self, settingName:str):
        self.__slave.SendSettingUpdateByName(settingName)

class Players():
    def __init__(self):
        self.__playerList = dict()
        self.__nbPlayers = 0

    def AddPlayer(self, slave:Slave):
        newPlayer = Player()
        newPlayer.SetSlave(slave)
        newPlayer.Send("GREEN GOOD")
        self.__playerList[self.__nbPlayers] = newPlayer
        self.__nbPlayers += 1

    def GetPlayer(self, index:int):
        return self.__playerList[index]

playerList = Players()

turret:Slave
########################

###   INIT SYSTEM    ###

def initNotifLaser(slaveID:int):
    pass

########################

### TARGETING SYSTEM ###

targetting = False
step = 0
speed_setting:Setting
target_side = ""
left_trigger:Setting
right_trigger:Setting

LASER_DETECTED = 2

def targetRight(window:sg.Window):
    STR.ConfigDirectSettingUpdate(2, 1, LASER_DETECTED) #A améliorer
    
    STR.SendUpdateSetting(STR.GetSlaveSettings()[2][2])
    
    global targetting
    global target_side
    global speed_setting
    global step
    global left_trigger
    global right_trigger

    targetting = True
    target_side = "R"
    step = 0

    #speed_setting = STR.GetSlaveSettings()[5][0] #A améliorer
    #speed_setting.SetValue(255)

    #left_trigger = STR.GetSlaveSettings()[5][1]
    #right_trigger = STR.GetSlaveSettings()[5][3]

    #STR.SendUpdateSetting(speed_setting)
    #STR.SendUpdateSetting(right_trigger)

    turret.SendSettingUpdateByName("SPEED", 255)
    turret.SendSettingUpdateByName("DROITE")

    display.UpdateSetting((speed_setting.GetSlaveID(), speed_setting.GetRef()))

display.AddPreLayout((IDP_BUTTON, "targetRight", targetRight))

def notifLaser(slaveID:int):

    global step
    global target_side
    global targetting

    if targetting:
        if step == 0:
            #speed_setting.SetValue(128)
            #STR.SendUpdateSetting(speed_setting)
            turret.SendSettingUpdateByName("SPEED", 128)

            if target_side == "R":
                #STR.SendUpdateSetting(left_trigger)
                turret.SendSettingUpdateByName("GAUCHE")
            elif target_side == "L":
                #STR.SendUpdateSetting(left_trigger)
                turret.SendSettingUpdateByName("DROITE")
            step = 3

        elif step == 3:
            #speed_setting.SetValue(64)
            #STR.SendUpdateSetting(speed_setting)
            turret.SendSettingUpdateByName("SPEED", 64)

            if target_side == "R":
                #STR.SendUpdateSetting(right_trigger)
                turret.SendSettingUpdateByName("DROITE")
            elif target_side == "L":
                #STR.SendUpdateSetting(left_trigger)
                turret.SendSettingUpdateByName("GAUCHE")
            step = 4

        elif step == 4:
            step = 0
            target_side = ""
            targetting = False
            STR.RemoveDirectSettingUpdateConfig(2, 1, LASER_DETECTED)
            STR.SendUpdateSetting(STR.GetSlaveSettings()[4][3])
            #STR.SendUpdateSetting(STR.GetSlaveSettings()[5][2])
            #STR.SendUpdateSetting(STR.GetSlaveSettings()[5][4])
        
        display.UpdateSetting((speed_setting.GetSlaveID(), speed_setting.GetRef()))

    print("Laser Detected")
    print(slaveID)

########################

#STR.AddNotifCallback(0x05, notifLaser)


def DeskCallback(slave:Slave):
    playerList.AddPlayer(slave)

STR.SendBridgeInitRequest(2, b'Desk', DeskCallback)


def TurretCallback(slave:Slave):
    global turret
    turret = slave

STR.SendBridgeInitRequest(1, b'Turret', TurretCallback)


def SendInitRequest(window:sg.Window):
    STR.SendInitRequest(0x42)

display.AddPreLayout((IDP_BUTTON,"Init", SendInitRequest))

display.UpdateLayout(None)

while True:
    STR.Update()
