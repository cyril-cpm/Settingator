from Settingator import *
from PySerialCommunicator import *
from PySimpleGUIDisplay import *


com = SerialCTR("COM8")

display = PySimpleGUIDisplay()

STR = Settingator(com, display)

###   GAME SYSTEM    ###

NUMBER_PLAYER = 2

GS_INIT = 0

gameStep = GS_INIT

class Player():
    def __init__(self):
        self.__score = 0
        self.__bonus = 0
        self.__fail = 0
        self.__slave = None
        self.__order = 0

    def SetSlave(self, slave:Slave):
        self.__slave = slave

    def Send(self, settingName:str):
        self.__slave.SendSettingUpdateByName(settingName)

    def GetSlave(self):
        return self.__slave

    def GetOrder(self):
        return self.__order
    
    def SetOrder(self, order:int):
        self.__order = order

class Players():
    def __init__(self):
        self.__playerList = dict()
        self.__nbPlayers = 0
        self.__orderedPlayerList = dict()
        self.__numberOrderedPlayer = 0

    def AddPlayer(self, slave:Slave):
        newPlayer = Player()
        newPlayer.SetSlave(slave)
        newPlayer.Send("GREEN LOADING")
        self.__playerList[self.__nbPlayers] = newPlayer
        self.__nbPlayers += 1

    def GetPlayer(self, index:int):
        return self.__playerList[index]
    
    def GetPlayerByOrder(self, orderedIndex:int):
        return self.__orderedPlayerList[orderedIndex]
    
    def GetPlayerBySlaveID(self, slaveID:int):
        for index in self.__playerList:
            if self.__playerList[index].GetSlave().GetID() == slaveID:
                return self.__playerList[index]
    
    def AddOrderedPlayer(self, player:Player):
        self.__numberOrderedPlayer += 1
        self.__orderedPlayerList[self.__numberOrderedPlayer] = player
        player.Send("GREEN GOOD")
        player.SetOrder(self.__numberOrderedPlayer)
        self.__AddToPreLayout(player)
        display.UpdateLayout(STR.GetSlaveSettings())

    def GetNumberOfOrderedPlayer(self):
        return self.__numberOrderedPlayer
    
    def __AddToPreLayout(self, player:Player):
        frameName:str = "Player " + str(self.__numberOrderedPlayer) + " : Slave " + str(player.GetSlave().GetID())
        display.AddPreLayout((IDP_FRAME, frameName, [(IDP_BUTTON, "target", lambda window : targetPlayer(window, player.GetOrder()))]))

playerList = Players()

turret:Slave
########################


### TARGETING SYSTEM ###

TP_START = 0
TP_END = 5

turretPos = TP_START

targetting = False
step = 0
target_side = ""
targetedPlayer:Player = None

LASER_DETECTED = 2

def targetRight(window:sg.Window):
    STR.ConfigDirectSettingUpdate(2, 1, LASER_DETECTED) #A améliorer
    
    STR.SendUpdateSetting(STR.GetSlaveSettings()[2][2])
    
    global targetting
    global target_side
    global step

    targetting = True
    target_side = "R"
    step = 0

    turret.SendSettingUpdateByName("SPEED", 255)
    turret.SendSettingUpdateByName("DROITE")

    display.UpdateSetting(turret.GetSettingByName("SPEED"))

display.AddPreLayout((IDP_BUTTON, "targetRight", targetRight))


def targetPlayer(windows:sg.Window, orderedPlayer:int):
    STR.AddNotifCallback(0x05, notifLaser)
    player:Player = playerList.GetPlayerByOrder(orderedPlayer)
    
    STR.ConfigDirectSettingUpdate(2, 1, LASER_DETECTED) #A améliorer
    player.GetSlave().ConfigDirectSettingUpdate(turret, LASER_DETECTED)
    
    player.Send("RED ACCEL LOADING")
    
    print("targetting player " + str(orderedPlayer))
    print("turretPos : " + str(turretPos))

    global targetting
    global target_side
    global targetedPlayer
    global step

    step = 0
    targetedPlayer = player

    turret.SendSettingUpdateByName("SPEED", 255)

    if turretPos < orderedPlayer:
        targetting = True
        target_side = "R"
        turret.SendSettingUpdateByName("DROITE")
        print("turning right")
    
    elif orderedPlayer < turretPos:
        targetting = True
        target_side = "L"
        turret.SendSettingUpdateByName("GAUCHE")
        print("turning left")

    display.UpdateSetting(turret.GetSettingByName("SPEED"))

def initPlayer(window:sg.Window):
    STR.AddNotifCallback(0x05, initNotifLaser)

    turret.SendSettingUpdateByName("SPEED", 255)
    turret.SendSettingUpdateByName("DROITE")

display.AddPreLayout((IDP_BUTTON, "initPlayer", initPlayer))

def notifLaser(slaveID:int):

    global step
    global target_side
    global targetting
    global turretPos

    if targetting and slaveID == targetedPlayer.GetSlave().GetID():
        print("targetedPlayer is " + str(targetedPlayer.GetOrder()))
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

            targetedPlayer.Send("RED_BAD")
            turret.SendSettingUpdateByName("STOP")
            turret.SendSettingUpdateByName("SHOOT")
            turretPos = targetedPlayer.GetOrder()
            #STR.SendUpdateSetting(STR.GetSlaveSettings()[5][2])
            #STR.SendUpdateSetting(STR.GetSlaveSettings()[5][4])
        
        display.UpdateSetting(turret.GetSettingByName("SPEED"))

    print("Laser Detected")
    print(slaveID)

########################

###   INIT SYSTEM    ###

def initNotifLaser(slaveID:int):
    playerList.AddOrderedPlayer(playerList.GetPlayerBySlaveID(slaveID))

    if playerList.GetNumberOfOrderedPlayer() >= NUMBER_PLAYER:
        turret.SendSettingUpdateByName("STOP")
        global turretPos

        turretPos = TP_END

########################

STR.AddNotifCallback(0x05, notifLaser)


def DeskCallback(slave:Slave):
    playerList.AddPlayer(slave)

STR.SendBridgeInitRequest(2, b'Desk', DeskCallback, NUMBER_PLAYER)


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
