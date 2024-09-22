from Settingator import *
from PySerialCommunicator import *
from PySimpleGUIDisplay import *
import csv
import random
import time
import multiprocessing
import pyttsx3

com:SerialCTR

display:PySimpleGUIDisplay

STR:Settingator

###   GAME SYSTEM    ###

NUMBER_PLAYER = 2

GS_INIT = 0
GS_WAITING_TO_START = 1
GS_ABOUT_TO_READ = 2
GS_READING = 3
GS_WAITING = 4
GS_REWARDING = 5
GS_FINISHED = 6
GS_FINISHED_READING = 7

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



NULL = 0
AUTO = 1
MANUAL = 2

class Game():
    def __init__(self):
        self.__questionPool = []
        self.__question = 0
        self.__mode = NULL
        self.__speakingQueue = multiprocessing.Queue()
        self.__gameStepLock = multiprocessing.Lock()
        self.__gameStep = multiprocessing.Value('i', GS_INIT)
        self.__finishedReadingTimestamp = 0
        
    def Start(self, mode:int):
        self.__mode = mode

        display.RemovePreLayout(startGameAutoButton)
        display.RemovePreLayout(startGameManualButton)
        display.UpdateLayout(STR.GetSlaveSettings())

        allQuestion = []
        
        with open("question.csv") as questionFile:
            csvContent = csv.reader(questionFile, delimiter=';')

            for row in csvContent:
                allQuestion.append(row)

        random.seed(time.time())

        for index in range(1, 10, 1):
            questionNo = random.randint(0, allQuestion.__len__() - 1)
            self.__questionPool.append(allQuestion[questionNo])

        self.__gameStep.value = GS_ABOUT_TO_READ

    def Update(self):
        if self.__mode == AUTO:
            if self.__gameStep.value == GS_ABOUT_TO_READ:
                self.Ask("Coucou Yolo")

            elif self.__gameStep.value == GS_READING:
                pass

            elif self.__gameStep.value == GS_FINISHED_READING:
                print("finishedReading")

                self.__gameStep.value = GS_WAITING
                self.__finishedReadingTimestamp = time.time()

            elif self.__gameStep.value == GS_WAITING:

                if time.time() - self.__finishedReadingTimestamp >= 10:
                    print("starting rewarding")
                    self.__gameStep.value = GS_REWARDING

            elif self.__gameStep.value == GS_REWARDING:
                if self.__question == 9:
                    self.__gameStep.value = GS_FINISHED
                else:
                    self.__question += 1
                    self.__gameStep.value = GS_ABOUT_TO_READ

            elif self.__gameStep.value == GS_FINISHED:
                self.Say("Les questions sont finies")
            
        elif self.__mode == MANUAL:
            pass

    def GetSpeakingQueue(self):
        return self.__speakingQueue
    
    def GetGameStepLock(self):
        return self.__gameStepLock
    
    def GetGameStep(self):
        return self.__gameStep
    
    def SetGameStep(self, gameStep):
        self.__gameStep.value = gameStep

    def Ask(self, sentence:str):
        self._Speak(sentence, True)

    def Say(self, sentence:str):
        self._Speak(sentence, False)

    def _Speak(self, sentence:str, isQuestion:bool = True):
        self.__speakingQueue.put((sentence, isQuestion))

game:Game          
        
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
        display.AddPreLayout(startGameAutoButton)
        display.AddPreLayout(startGameManualButton)
        game.SetGameStep(GS_WAITING_TO_START)
        display.UpdateLayout(STR.GetSlaveSettings())

########################

### SPEAKING PROCESS ###

def onStart(gameStep):
    gameStep.value = GS_READING

def onEnd(gameStep):
    gameStep.value = GS_FINISHED_READING

def speakingProcessFunction(queue:multiprocessing.Queue, gameStep):
    engine = pyttsx3.init()
    engine.setProperty('volume', 0.5)

    #engine.connect('started-utterance', lambda name : onStart(gameStep))
    #engine.connect('finished-utterance', lambda name : onEnd(gameStep))

    voices = engine.getProperty('voices')

    for voice in voices:
        if "French" in voice.name:
            engine.setProperty("voice", voice.id)
            break

    while True:
        sentence, isQuestion = queue.get()
        engine.say(sentence)
        if isQuestion:
            gameStep.value = GS_READING
        engine.runAndWait()
        if isQuestion:
            gameStep.value = GS_FINISHED_READING

########################

def DeskCallback(slave:Slave):
    playerList.AddPlayer(slave)

def TurretCallback(slave:Slave):
    global turret
    turret = slave

if __name__ == "__main__":
    game = Game()

    speakingProcess = multiprocessing.Process(target=speakingProcessFunction, args=(game.GetSpeakingQueue(), game.GetGameStep()))
    speakingProcess.start()

    com = SerialCTR("COM4")

    display = PySimpleGUIDisplay()
    
    STR = Settingator(com, display)

    STR.AddNotifCallback(RED_BUTTON, lambda slaveID : playerPressButton(slaveID, RED_BUTTON))
    STR.AddNotifCallback(GREEN_BUTTON, lambda slaveID : playerPressButton(slaveID, GREEN_BUTTON))
    STR.AddNotifCallback(BLUE_BUTTON, lambda slaveID : playerPressButton(slaveID, BLUE_BUTTON))
    STR.AddNotifCallback(YELLOW_BUTTON, lambda slaveID : playerPressButton(slaveID, YELLOW_BUTTON))

    STR.AddNotifCallback(LASER_NOTIF, notifLaser)
    STR.SendBridgeInitRequest(1, b'Turret', TurretCallback)
    STR.SendBridgeInitRequest(2, b'Desk', DeskCallback, NUMBER_PLAYER)

    display.AddPreLayout(startGameAutoButton)
    display.AddPreLayout(startGameManualButton)
    display.AddPreLayout(InitPlayerButton)
    display.UpdateLayout(None)

    while True:
        STR.Update()
        game.Update()
