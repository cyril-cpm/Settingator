from Settingator import *
from PySerialCommunicator import *
from PySimpleGUIDisplay import *
import csv
import random
import time

com = SerialCTR("COM8")

display = PySimpleGUIDisplay()

STR = Settingator(com, display)

###   GAME SYSTEM    ###

NUMBER_PLAYER = 2

GS_INIT = 0
GS_WAITING_TO_START = 1
GS_ABOUT_TO_READ = 2
GS_READING = 3
GS_WAITING = 4
GS_REWARDING = 5
GS_FINISHED = 6

gameStep = GS_INIT

RED_BUTTON = 13
GREEN_BUTTON = 12
YELLOW_BUTTON = 14
BLUE_BUTTON = 27

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

def playerPressButton(slaveID:int, button:int):
    #player:Player = playerList.GetPlayerBySlaveID(slaveID)

    logString = "Slave "+str(slaveID) + " pressed button "

    if button == RED_BUTTON:
        logString += "red"
    elif button == GREEN_BUTTON:
        logString += "green"
    elif button == BLUE_BUTTON:
        logString += "blue"
    elif button == YELLOW_BUTTON:
        logString += "yellow"

    print(logString)

STR.AddNotifCallback(RED_BUTTON, lambda slaveID : playerPressButton(slaveID, RED_BUTTON))
STR.AddNotifCallback(GREEN_BUTTON, lambda slaveID : playerPressButton(slaveID, GREEN_BUTTON))
STR.AddNotifCallback(BLUE_BUTTON, lambda slaveID : playerPressButton(slaveID, BLUE_BUTTON))
STR.AddNotifCallback(YELLOW_BUTTON, lambda slaveID : playerPressButton(slaveID, YELLOW_BUTTON))

NULL = 0
AUTO = 1
MANUAL = 2

class Game():
    def __init__(self):
        self.__questionPool = []
        self.__question = 0
        self.__mode = NULL
        
    def Start(self, mode:int):
        self.__mode = mode

        display.RemovePreLayout(startGameAutoButton)
        display.RemovePreLayout(startGameManualButton)
        display.Update(STR.GetSlaveSettings())

        allQuestion = []
        
        with open("question.csv") as questionFile:
            csvContent = csv.reader(questionFile, delimiter=';')

            for row in csvContent:
                allQuestion.append(row)

        random.seed(time.time())

        for index in range(1, 10, 1):
            questionNo = random.randint(0, allQuestion.__len__() - 1)
            self.__questionPool.append(allQuestion[questionNo])

        gameStep == GS_ABOUT_TO_READ

    def Update(self):
        if self.__mode == AUTO:
            if gameStep == GS_ABOUT_TO_READ:
                gameStep == GS_READING

            elif gameStep == GS_READING:
                gameStep == GS_WAITING

            elif gameStep == GS_WAITING:
                gameStep == GS_REWARDING

            elif gameStep == GS_REWARDING:
                if self.__question == 9:
                    gameStep == GS_FINISHED
                else:
                    self.__question += 1
                    gameStep == GS_ABOUT_TO_READ

            elif gameStep == GS_FINISHED:
                pass
            
        elif self.__mode == MANUAL:
            pass

game = Game()           
        

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
LASER_NOTIF = 0x05

def targetPlayer(windows:sg.Window, orderedPlayer:int):
    
    global targetting
    global target_side
    global targetedPlayer
    global step

    STR.AddNotifCallback(LASER_NOTIF, notifLaser)
    targetedPlayer = playerList.GetPlayerByOrder(orderedPlayer)
    
    targetedPlayer.GetSlave().ConfigDirectSettingUpdate(turret, LASER_DETECTED)
    
    targetedPlayer.Send("RED ACCEL LOADING")
    
    print("targetting player " + str(targetedPlayer.GetOrder()))
    print("turretPos : " + str(turretPos))


    step = 0

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

def notifLaser(slaveID:int):

    global step
    global target_side
    global targetting
    global turretPos
    global targetedPlayer

    if targetting and slaveID == targetedPlayer.GetSlave().GetID():
        print("targetedPlayer is " + str(targetedPlayer.GetOrder()))
        if step == 0:
            turret.SendSettingUpdateByName("SPEED", 128)

            if target_side == "R":
                turret.SendSettingUpdateByName("GAUCHE")
            elif target_side == "L":
                turret.SendSettingUpdateByName("DROITE")
            step = 3

        elif step == 3:
            turret.SendSettingUpdateByName("SPEED", 64)

            if target_side == "R":
                turret.SendSettingUpdateByName("DROITE")
            elif target_side == "L":
                turret.SendSettingUpdateByName("GAUCHE")
            step = 4

        elif step == 4:
            step = 0
            target_side = ""
            targetting = False

            targetedPlayer.GetSlave().RemoveDirectSettingUpdateConfig(turret, LASER_DETECTED)
            targetedPlayer.Send("RED BAD")
            turret.SendSettingUpdateByName("SHOOT")
            targetedPlayer = None
        
        display.UpdateSetting(turret.GetSettingByName("SPEED"))

    print("Laser Detected")
    print(slaveID)
    turretPos = playerList.GetPlayerBySlaveID(slaveID).GetOrder()

########################

###   INIT SYSTEM    ###

def startGameAuto(window:sg.Window):
    game.Start(AUTO)

startGameAutoButton = (IDP_BUTTON, "startGameAuto", startGameAuto)

def startGameManual(window:sg.Window):
    game.Start(MANUAL)

startGameManualButton = (IDP_BUTTON, "startGameManual", startGameManual)

def initPlayer(window:sg.Window):
    STR.AddNotifCallback(0x05, initNotifLaser)

    turret.SendSettingUpdateByName("SPEED", 255)
    turret.SendSettingUpdateByName("DROITE")

InitPlayerButton = (IDP_BUTTON, "initPlayer", initPlayer)

def initNotifLaser(slaveID:int):
    playerList.AddOrderedPlayer(playerList.GetPlayerBySlaveID(slaveID))

    if playerList.GetNumberOfOrderedPlayer() >= NUMBER_PLAYER:
        turret.SendSettingUpdateByName("STOP")
        display.RemovePreLayout(InitPlayerButton)
        global turretPos
        global gameStep

        turretPos = TP_END
        display.AddPreLayout(startGameButton)
        gameStep = GS_WAITING_TO_START
        display.UpdateLayout(STR.GetSlaveSettings())

display.AddPreLayout(InitPlayerButton)

########################

STR.AddNotifCallback(LASER_NOTIF, notifLaser)


def DeskCallback(slave:Slave):
    playerList.AddPlayer(slave)

STR.SendBridgeInitRequest(2, b'Desk', DeskCallback, NUMBER_PLAYER)


def TurretCallback(slave:Slave):
    global turret
    turret = slave

STR.SendBridgeInitRequest(1, b'Turret', TurretCallback)


display.UpdateLayout(None)

while True:
    STR.Update()
    game.Update()
