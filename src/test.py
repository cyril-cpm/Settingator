from Settingator import *
from PySerialCommunicator import *
from PySimpleGUIDisplay import *
import csv
import random
import time
import multiprocessing
import pyttsx3
import pygame.mixer as mx

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
GS_FINISHED_REWARDING = 8

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
        self.__answeredCurrentQuestion = False
        self.__lastAnswer = None

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

    def CanAnswer(self):
        return not self.__answeredCurrentQuestion
    
    def ResetAnswered(self):
        self.SetAnswered(False)
        self.__lastAnswer = None

    def SetAnswered(self, value:bool = True):
        self.__answeredCurrentQuestion = value

    def SetLastAnswer(self, value:int):
        self.__lastAnswer = value
        self.SetAnswered()

    def GetLastAnswer(self):
        return self.__lastAnswer
    
    def IncreaseGood(self):
        self.__score += 1
    
    def IncreaseFail(self):
        self.__fail += 1

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
        
        return None
    
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

    def AllAnswered(self):
        allAnswered = True

        for player in self.__playerList:
            if self.__playerList[player].CanAnswer():
                allAnswered = False

        return allAnswered
    
    def SendAll(self, command):
        for player in self.__playerList:
            self.__playerList[player].Send(command)

playerList = Players()

turret:Slave

def playerPressButton(slaveID:int, button:int):
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

    player:Player = playerList.GetPlayerBySlaveID(slaveID)

    if player != None:
        if player.CanAnswer() and game.CanAnswer():
            if button == RED_BUTTON:
                player.SetLastAnswer(0)
            elif button == GREEN_BUTTON:                
                player.SetLastAnswer(1)
            elif button == YELLOW_BUTTON:
                player.SetLastAnswer(2)
            elif button == BLUE_BUTTON:
                player.SetLastAnswer(3)

            player.Send("BLUE FROZEN")


NULL = 0
AUTO = 1
MANUAL = 2

RED_COLOR = "#FF0000"
BLUE_COLOR = "#0000FF"
GREEN_COLOR = "#00FF00"
YELLOW_COLOR = "#EEEE00"
DARK_GREY_COLOR = "#222222"
BLACK_COLOR = "#000000"
LIGHT_GREY_COLOR = "#666666"
GOLD_COLOR = "#D3AF37"
SILVER_COLOR = "#A8A9AD"
BRONZE_COLOR = "#49371B"
DARK_RED_COLOR = "#111111"

class QuestionAndScoreDisplay():
    def __init__(self):

        self.__PSGLayout = [[]]

        dummyWindow = sg.Window("",[[]], location=(-1, 0), finalize=True, size=(0,0), no_titlebar=True)
        dummyWindow.Maximize()

        self.__screenWidth, self.__screenHeight = dummyWindow.Size

        dummyWindow.Close()

        #### QUESTION DISPLAY ####

        questionDisplayLayout = [[],[]]

        self.__questionText = sg.Text("", background_color=DARK_GREY_COLOR, expand_x=True, justification="center")
        questionFrameLayout = [[sg.VPush(background_color=DARK_GREY_COLOR)], [self.__questionText], [sg.VPush(background_color=DARK_GREY_COLOR)]]
        questionFrame = sg.Frame("", questionFrameLayout, border_width=0, background_color=DARK_GREY_COLOR, expand_y=True, pad=10, size=(self.__screenWidth - 20, 1))

        self.__ansAText = sg.Text("", background_color=RED_COLOR, expand_x=True, justification="center")
        self.__ansBText = sg.Text("", background_color=GREEN_COLOR, expand_x=True, justification="center")
        self.__ansCText = sg.Text("", background_color=YELLOW_COLOR, expand_x=True, justification="center")
        self.__ansDText = sg.Text("", background_color=BLUE_COLOR, expand_x=True, justification="center")

        ansAFrame = sg.Frame("", [[sg.VPush(background_color=RED_COLOR)], [self.__ansAText], [sg.VPush(background_color=RED_COLOR)]], border_width=0, background_color=RED_COLOR, size=(int(self.__screenWidth/2) - 20,1), expand_y=True, pad=10)
        ansBFrame = sg.Frame("", [[sg.VPush(background_color=GREEN_COLOR)], [self.__ansBText], [sg.VPush(background_color=GREEN_COLOR)]], border_width=0, background_color=GREEN_COLOR, size=(int(self.__screenWidth/2) - 20,1), expand_y=True, pad=10)
        ansCFrame = sg.Frame("", [[sg.VPush(background_color=YELLOW_COLOR)], [self.__ansCText], [sg.VPush(background_color=YELLOW_COLOR)]], border_width=0, background_color=YELLOW_COLOR, size=(int(self.__screenWidth/2) - 20,1), expand_y=True, pad=10)
        ansDFrame = sg.Frame("", [[sg.VPush(background_color=BLUE_COLOR)], [self.__ansDText], [sg.VPush(background_color=BLUE_COLOR)]], border_width=0, background_color=BLUE_COLOR, size=(int(self.__screenWidth/2) - 20,1), expand_y=True, pad=10)

        answerFrameLayout = [[],[]]
        answerFrameLayout[0].append(ansAFrame)
        answerFrameLayout[0].append(ansBFrame)
        answerFrameLayout[1].append(ansCFrame)
        answerFrameLayout[1].append(ansDFrame)

        answerFrame = sg.Frame("", answerFrameLayout, border_width=0, background_color=LIGHT_GREY_COLOR, size=(self.__screenWidth - 20,1), expand_y=True, pad=10)

        questionDisplayLayout[0].append(questionFrame)
        questionDisplayLayout[1].append(answerFrame)
        self.__questionDisplayFrame = sg.Column(questionDisplayLayout, expand_x=True, expand_y=True, background_color=BLACK_COLOR, pad=0, visible=False)

        self.__PSGLayout[0].append(self.__questionDisplayFrame)

        ########################

        #### SCORE DISPLAY #####

        self.__labelWidth = int(self.__screenWidth/3)
        self.__labelHeight = int(self.__screenHeight/10)

        length = sg.Text.string_width_in_pixels("_ 3000", "WWWWWWWWWWWWWWW")
        
        width = int(self.__labelWidth * 2.0/3.0)
        fontSize = int(3000 * (width / length))

        nameFont = "_ " + str(fontSize)
        scoreFont = "Inconsolata " + str(fontSize)

        self.__firstPlayerName = self.__newPlayerName(GOLD_COLOR, nameFont)
        self.__secondPlayerName = self.__newPlayerName(SILVER_COLOR, nameFont)
        self.__thirdPlayerName = self.__newPlayerName(BRONZE_COLOR, nameFont)
        self.__fourthPlayerName = self.__newPlayerName(DARK_RED_COLOR, nameFont)

        self.__firstPlayerGood = self.__newPlayerScore(GOLD_COLOR, GREEN_COLOR, scoreFont)
        self.__secondPlayerGood = self.__newPlayerScore(SILVER_COLOR, GREEN_COLOR, scoreFont)
        self.__thirdPlayerGood = self.__newPlayerScore(BRONZE_COLOR, GREEN_COLOR, scoreFont)
        self.__fourthPlayerGood = self.__newPlayerScore(DARK_RED_COLOR, GREEN_COLOR, scoreFont)

        self.__firstPlayerBad = self.__newPlayerScore(GOLD_COLOR, RED_COLOR, scoreFont)
        self.__secondPlayerBad = self.__newPlayerScore(SILVER_COLOR, RED_COLOR, scoreFont)
        self.__thirdPlayerBad = self.__newPlayerScore(BRONZE_COLOR, RED_COLOR, scoreFont)
        self.__fourthPlayerBad = self.__newPlayerScore(DARK_RED_COLOR, RED_COLOR, scoreFont)

        self.__firstPlayerTotal = self.__newPlayerScore(GOLD_COLOR, YELLOW_COLOR, scoreFont)
        self.__secondPlayerTotal = self.__newPlayerScore(SILVER_COLOR, YELLOW_COLOR, scoreFont)
        self.__thirdPlayerTotal = self.__newPlayerScore(BRONZE_COLOR, YELLOW_COLOR, scoreFont)
        self.__fourthPlayerTotal = self.__newPlayerScore(DARK_RED_COLOR, YELLOW_COLOR, scoreFont)

        firstPlayer = self.__newPlayerFrame(GOLD_COLOR, self.__firstPlayerName, self.__firstPlayerGood, self.__firstPlayerBad, self.__firstPlayerTotal)
        
        secondPlayer = self.__newPlayerFrame(SILVER_COLOR, self.__secondPlayerName, self.__secondPlayerGood, self.__secondPlayerBad, self.__secondPlayerTotal)
        
        thirdPlayer = self.__newPlayerFrame(BRONZE_COLOR, self.__thirdPlayerName, self.__thirdPlayerGood, self.__thirdPlayerBad, self.__thirdPlayerTotal)
        
        fourthPlayer = self.__newPlayerFrame(DARK_RED_COLOR, self.__fourthPlayerName, self.__fourthPlayerGood, self.__fourthPlayerBad, self.__fourthPlayerTotal)

        scoreLayout = [[firstPlayer], 
                       [secondPlayer],
                       [thirdPlayer],
                       [fourthPlayer]]
        
        scoreFrame = sg.Frame("", scoreLayout, border_width=0, background_color=LIGHT_GREY_COLOR, size=(self.__labelWidth, 4 * (self.__labelHeight + 20)), element_justification="center")

        scoreDisplayLayout = [[sg.VPush(background_color=BLACK_COLOR)],
                              [scoreFrame],
                              [sg.VPush(background_color=BLACK_COLOR)]]

        self.__scoreDisplayFrame = sg.Frame("", scoreDisplayLayout, border_width=0, background_color=BLACK_COLOR, pad=0, element_justification="center", visible=False, size=(self.__screenWidth, self.__screenHeight))

        self.__PSGLayout[0].append(self.__scoreDisplayFrame)

        ########################

        ####### MAXIMIZE #######

        self.__maximizeButton = sg.Button("Maximize", key=self.__maximizeDisplay, visible=False)
        self.__PSGLayout[0].append(self.__maximizeButton)

        ########################

        self.__PSGWindow = sg.Window('Display', self.__PSGLayout, location=(-1, 0), grab_anywhere=True, element_justification='left', finalize=True, background_color=BLACK_COLOR, element_padding=0, return_keyboard_events=True, no_titlebar=True, size=(0, 0))
        self.__PSGWindow.Maximize()

        return

    def __newPlayerName(self, color, font):
        return sg.Text("", background_color=color, expand_x=True, font=font)
    
    def __newPlayerScore(self, bgColor, fgColor, font):
        return sg.Text("", background_color=bgColor, text_color=fgColor, font=font)
    
    def __newPlayerFrame(self, color, name, good, bad, total):
        return sg.Frame("", [[sg.VPush(background_color=color)],
                                 [sg.Column([[name, good, bad, total]], expand_x=True, pad=(40, 0), background_color=color)],
                                 [sg.VPush(background_color=color)]],
                                 background_color=color, size=(self.__labelWidth-20, self.__labelHeight), pad=10)

    def Update(self):
        event, values = self.__PSGWindow.read(0)
        if event == 'Escape:27':
            self.__PSGWindow.Close()
            quit()

        if callable(event):
            event()

    def SetQuestion(self, question, ansA, ansB, ansC, ansD):

        questionLength = sg.Text.string_width_in_pixels("_ 3000", question)
        width = self.__screenWidth - 80
        fontSize = int(3000 * (width / questionLength))
        fontStr = "_ "+str(fontSize
                           )
        self.__questionText.update(value=question, font=fontStr)

        lengthA = sg.Text.string_width_in_pixels("_ 3000", ansA)
        lengthB = sg.Text.string_width_in_pixels("_ 3000", ansB)
        lengthC = sg.Text.string_width_in_pixels("_ 3000", ansC)
        lengthD = sg.Text.string_width_in_pixels("_ 3000", ansD)

        lengthiest = lengthA
        if lengthB > lengthiest:
            lengthiest = lengthB
        if lengthC > lengthiest:
            lengthiest = lengthC
        if lengthD > lengthiest:
            lengthiest = lengthD
        
        width = self.__screenWidth/2 - 80
        fontSize = int(3000 * (width / lengthiest))
        fontStr = "_ "+str(fontSize)

        self.__ansAText.update(value=ansA, font=fontStr)
        self.__ansBText.update(value=ansB, font=fontStr)
        self.__ansCText.update(value=ansC, font=fontStr)
        self.__ansDText.update(value=ansD, font=fontStr)

        self.__scoreDisplayFrame.update(visible=False)
        self.__questionDisplayFrame.update(visible=True)

    def SetScore(self, fiName, fiGood, fiBad, sName, sGood, sBad, tName, tGood, tBad, foName, foGood, foBad):
        self.__firstPlayerName.update(fiName)
        self.__secondPlayerName.update(sName)
        self.__thirdPlayerName.update(tName)
        self.__fourthPlayerName.update(foName)

        self.__transformAndUpdate(fiGood, self.__firstPlayerGood)
        self.__transformAndUpdate(sGood, self.__secondPlayerGood)
        self.__transformAndUpdate(tGood, self.__thirdPlayerGood)
        self.__transformAndUpdate(foGood, self.__fourthPlayerGood)

        self.__transformAndUpdate(fiBad, self.__firstPlayerBad)
        self.__transformAndUpdate(sBad, self.__secondPlayerBad)
        self.__transformAndUpdate(tBad, self.__thirdPlayerBad)
        self.__transformAndUpdate(foBad, self.__fourthPlayerBad)

        self.__transformAndUpdate(fiGood - fiBad, self.__firstPlayerTotal)
        self.__transformAndUpdate(sGood - sBad, self.__secondPlayerTotal)
        self.__transformAndUpdate(tGood - tBad, self.__thirdPlayerTotal)
        self.__transformAndUpdate(foGood - foBad, self.__fourthPlayerTotal)

        self.__questionDisplayFrame.update(visible=False)
        self.__scoreDisplayFrame.update(visible=True)

    def __transformAndUpdate(self, value, sgText:sg.Text):
        valueStr = ""

        if value >= 10:
            valueStr = "  " + str(value)
        elif value >= 0:
            valueStr = "   " + str(value)
        elif value <= -10:
            valueStr = " " + str(value)
        elif value < 0:
            valueStr = "  " + str(value)

        sgText.update(valueStr)

    def __maximizeDisplay(self):
        self.__maximizeButton.update(visible=False)
        self.__PSGWindow.Maximize()

class Game():
    def __init__(self):
        self.__questionPool = []
        self.__question = 0
        self.__mode = NULL
        self.__speakingQueue = multiprocessing.Queue()
        self.__gameStepLock = multiprocessing.Lock()
        self.__gameStep = multiprocessing.Value('i', GS_INIT)
        self.__finishedReadingTimestamp = 0
        self.__currentQuestionGoodAnswer = 0
        self.__accelDone = False
        self.__questionAndScoreDisplay = QuestionAndScoreDisplay()
        #self.__questionAndScoreDisplay.SetScore("Bernard", 1, -3, "Jean-Dom'", 2, 17, "Bapt", 4, 4, "SheitMan", 8, 0)


        ### Sound Management ###
        mx.init(channels=1)
        self.__channel = mx.Channel(0)
        self.__goodSound = mx.Sound("good.wav")
        self.__badSound = mx.Sound("bad.wav")
        self.__waitingSound = mx.Sound("waiting.wav")
        self.__endWaitSound = mx.Sound("endWait.wav")

    def PlayGoodSound(self):
        self.__channel.play(self.__goodSound)

    def PlayBadSound(self):
        self.__channel.play(self.__badSound)

    def PlayWaitingSound(self):
        self.__channel.play(self.__waitingSound)

    def PlayEndWaitSound(self):
        self.__channel.play(self.__endWaitSound)

    def DisplayQuestion(question, order):
        pass
        
    def Start(self, mode:int):
        self.__mode = mode

        display.RemovePreLayout(startGameAutoButton)
        display.RemovePreLayout(startGameManualButton)
        display.UpdateLayout(STR.GetSlaveSettings())

        allQuestion = []
        
        with open("question.csv", encoding="utf-8") as questionFile:
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
                playerList.SendAll("BLUE LOADING")
                answerOrder = dict()
                answerOrdered = False
                index = 0
                alreadyPulled = dict()

                while not answerOrdered:
                    newIndex = random.randint(2, 5)

                    if not newIndex in alreadyPulled:
                        answerOrder[index] = newIndex
                        alreadyPulled[newIndex] = True

                        if newIndex == 2:
                            self.__currentQuestionGoodAnswer = index

                        index += 1
                        
                        if index >= 4:
                            answerOrdered = True
                
                question = self.__questionPool[self.__question]

                #game.DisplayQuestion(question, answerOrder)

                questionStr = question[1] + " Réponse A: " + question[answerOrder[0]] + ", Réponse B:" + question[answerOrder[1]] + ", Réponse C: " + question[answerOrder[2]] + " Réponse D: " + question[answerOrder[3]] + " ?"
                self.Ask(questionStr)

            elif self.__gameStep.value == GS_READING:
                pass

            elif self.__gameStep.value == GS_FINISHED_READING:
                self.PlayWaitingSound()
                print("finishedReading")

                self.__gameStep.value = GS_WAITING
                self.__finishedReadingTimestamp = time.time()
                self.__accelDone = False

            elif self.__gameStep.value == GS_WAITING:
                if not self.__accelDone and time.time() - self.__finishedReadingTimestamp >= 7:
                    for playerIndex in range(1, NUMBER_PLAYER + 1):
                        player:Player = playerList.GetPlayerByOrder(playerIndex)

                        if player.CanAnswer():
                            player.Send("RED ACCEL LOADING")

                    self.__accelDone = True

                if time.time() - self.__finishedReadingTimestamp >= 10 or playerList.AllAnswered():
                    self.PlayEndWaitSound()
                    playerList.SendAll("BLUE FROZEN")
                    print("starting rewarding")
                    self.__gameStep.value = GS_REWARDING

            elif self.__gameStep.value == GS_REWARDING:
                if target.Reward(self.__currentQuestionGoodAnswer):
                    self.__gameStep.value = GS_FINISHED_REWARDING

            elif self.__gameStep.value == GS_FINISHED_REWARDING:
                time.sleep(3)

                for playerIndex in range(1, NUMBER_PLAYER + 1):
                    playerList.GetPlayerByOrder(playerIndex).ResetAnswered()

                if self.__question == 3:
                    self.__gameStep.value = GS_FINISHED
                else:
                    self.__question += 1
                    self.__gameStep.value = GS_ABOUT_TO_READ

            elif self.__gameStep.value == GS_FINISHED:
                self.Say("Les questions sont finies")
            
        elif self.__mode == MANUAL:
            pass

        self.__questionAndScoreDisplay.Update()

    def GetSpeakingQueue(self):
        return self.__speakingQueue
    
    def GetGameStepLock(self):
        return self.__gameStepLock
    
    def GetGameStepValue(self):
        return self.__gameStep
    
    def GetGameStep(self):
        return self.__gameStep

    def GetGameStepValue(self):
        return self.__gameStep.value
    
    def SetGameStep(self, gameStep):
        self.__gameStep.value = gameStep

    def Ask(self, sentence:str):
        self._Speak(sentence, True)

    def Say(self, sentence:str):
        self._Speak(sentence, False)

    def CanAnswer(self):
        gameStep = self.GetGameStepValue()

        return (gameStep == GS_READING or gameStep == GS_FINISHED_READING or gameStep == GS_WAITING)

    def _Speak(self, sentence:str, isQuestion:bool = True):
        self.__speakingQueue.put((sentence, isQuestion))

    def SetScoreDisplay(self, fiName, fiGood, fiBad, sName, sGood, sBad, tName, tGood, tBad, foName, foGood, foBad):
        self.__questionAndScoreDisplay.SetScore(fiName, fiGood, fiBad, sName, sGood, sBad, tName, tGood, tBad, foName, foGood, foBad)

    def SetQuestionDisplay(self, question, ansA, ansB, ansC, ansD):
        self.__questionAndScoreDisplay.SetQuestion(question, ansA, ansB, ansC, ansD)

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
targetDone = False
targetDoneTimestamp = 0

LASER_DETECTED = 2
LASER_NOTIF = 0x05

class Target():
    def __init__(self):
        self.__turretPos = TP_START
        self.__targetting = False
        self.__step = 0
        self.__target_side = ""
        self.__targetedPlayer:Player = None
        self.__targetDone = False
        self.__targetDoneTimestamp = 0
        self.__allRewarded = False
        self.__currentRewardingPlayer = 0

    def Reward(self, goodAnswer:int) -> bool:
        if not self.__allRewarded:
            if not self.__targetDone and not self.__targetting:
                targetPlayer(None, self.__currentRewardingPlayer+1)
            if self.__targetDone:
                if time.time() - self.__targetDoneTimestamp > 3:
                    playerToReward:Player = playerList.GetPlayerByOrder(self.__currentRewardingPlayer+1)
                    shoot = playerToReward.GetLastAnswer() == goodAnswer

                    if shoot:
                        playerToReward.IncreaseGood()
                        playerToReward.Send("GREEN GOOD")
                        game.PlayGoodSound()
                    else:
                        playerToReward.IncreaseFail()
                        playerToReward.Send("RED BAD")
                        turret.SendSettingUpdateByName("SHOOT")
                        game.PlayBadSound()

                    self.__currentRewardingPlayer += 1
                    self.__targetDone = False

                    if self.__currentRewardingPlayer == NUMBER_PLAYER:
                        self.__allRewarded = True
                        self.__currentRewardingPlayer = 0
        else:
            self.__allRewarded = False

        return self.__allRewarded

    def TargetPlayer(self, orderedPlayer:int):
        self.__targetDone = False
        STR.AddNotifCallback(LASER_NOTIF, self._notifLaser)
         
        self.__targetedPlayer = playerList.GetPlayerByOrder(orderedPlayer)
        self.__targetedPlayer.GetSlave().ConfigDirectSettingUpdate(turret, LASER_DETECTED)

        print("targetting player " + str(self.__targetedPlayer.GetOrder()))
        print("turretPos : " + str(self.__turretPos))

        self.__step = 0

        turret.SendSettingUpdateByName("SPEED", 255)

        if self.__turretPos < orderedPlayer:
            self.__targetting = True
            self.__target_side = "R"
            turret.SendSettingUpdateByName("DROITE")
            print("turning right")

        elif orderedPlayer < self.__turretPos:
            self.__targetting = True
            self.__target_side = "L"
            turret.SendSettingUpdateByName("GAUCHE")
            print("turning left")

        display.UpdateSetting(turret.GetSettingByName("SPEED"))
    
    def _notifLaser(self, slaveID):
        print("___notifLaser")
        if self.__targetting and slaveID == self.__targetedPlayer.GetSlave().GetID():
            print("targetedPlayer is " + str(self.__targetedPlayer.GetOrder()))
            if self.__step == 0:
                turret.SendSettingUpdateByName("SPEED", 128)

                if self.__target_side == "R":
                    turret.SendSettingUpdateByName("GAUCHE")
                elif self.__target_side == "L":
                    turret.SendSettingUpdateByName("DROITE")
                self.__step = 1

            elif self.__step == 1:
                turret.SendSettingUpdateByName("SPEED", 64)

                if self.__target_side == "R":
                    turret.SendSettingUpdateByName("DROITE")
                elif self.__target_side == "L":
                    turret.SendSettingUpdateByName("GAUCHE")
                self.__step = 2

            elif self.__step == 2:
                self.__step = 0
                self.__target_side = ""
                self.__targetting = False

                self.__targetedPlayer.GetSlave().RemoveDirectSettingUpdateConfig(turret, LASER_DETECTED)
                turret.SendSettingUpdateByName("STOP")
                self.__targetedPlayer = None
                self.__targetDone = True
                self.__targetDoneTimestamp = time.time()

            display.UpdateSetting(turret.GetSettingByName("SPEED"))

        print("Laser Detected")
        print(slaveID)

        self.__turretPos = playerList.GetPlayerBySlaveID(slaveID).GetOrder()

    def SetTurretPos(self, turretPos):
        self.__turretPos = turretPos

target = Target()

def targetPlayer(windows:sg.Window, orderedPlayer:int):
    target.TargetPlayer(orderedPlayer)

def notifLaser(slaveID:int):

    global step
    global target_side
    global targetting
    global turretPos
    global targetedPlayer
    global targetDone
    global targetDoneTimestamp

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
            targetedPlayer = None
            targetDone = True
            targetDoneTimestamp = time.time()
        
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

#TEST#

def testDisplayQuestion(window:sg.Window):
    game.SetQuestionDisplay("Quelle est la taille du continum espace temps dans la série blargblargblarg ?", "La réponse A", "La grosse réponse B", "repC", "Et non pas la D")

testDisplayQuestionButton = (IDP_BUTTON, "testDisplayQuestion", testDisplayQuestion)

def testDisplayScore(window:sg.Window):
    game.SetScoreDisplay("Bernard", 1, -3, "Jean-Dom'", 2, 17, "Bapt", 4, 4, "SheitMan", 8, 0)

testDisplayScoreButton = (IDP_BUTTON, "testDisplayScore", testDisplayScore)

######

def initNotifLaser(slaveID:int):
    playerList.AddOrderedPlayer(playerList.GetPlayerBySlaveID(slaveID))

    if playerList.GetNumberOfOrderedPlayer() >= NUMBER_PLAYER:
        turret.SendSettingUpdateByName("STOP")
        display.RemovePreLayout(InitPlayerButton)
        global turretPos
        global gameStep

        target.SetTurretPos(TP_END)
        display.AddPreLayout(startGameAutoButton)
        display.AddPreLayout(startGameManualButton)
        game.SetGameStep(GS_WAITING_TO_START)
        display.UpdateLayout(STR.GetSlaveSettings())

########################

### SPEAKING PROCESS ###

def speakingProcessFunction(queue:multiprocessing.Queue, gameStep):
    engine = pyttsx3.init()
    engine.setProperty('volume', 1)

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

    com = SerialCTR("COM3")

    display = PySimpleGUIDisplay()
    
    STR = Settingator(com, display)

    STR.AddNotifCallback(RED_BUTTON, lambda slaveID : playerPressButton(slaveID, RED_BUTTON))
    STR.AddNotifCallback(GREEN_BUTTON, lambda slaveID : playerPressButton(slaveID, GREEN_BUTTON))
    STR.AddNotifCallback(BLUE_BUTTON, lambda slaveID : playerPressButton(slaveID, BLUE_BUTTON))
    STR.AddNotifCallback(YELLOW_BUTTON, lambda slaveID : playerPressButton(slaveID, YELLOW_BUTTON))

    STR.AddNotifCallback(LASER_NOTIF, notifLaser)
    STR.SendBridgeInitRequest(1, b'Turret', TurretCallback)
    STR.SendBridgeInitRequest(2, b'Desk', DeskCallback, NUMBER_PLAYER)

    #display.AddPreLayout(startGameAutoButton)
    #display.AddPreLayout(startGameManualButton)
    display.AddPreLayout(InitPlayerButton)

    display.AddPreLayout(testDisplayScoreButton)
    display.AddPreLayout(testDisplayQuestionButton)

    display.UpdateLayout(None)
    
    game = Game()

    speakingProcess = multiprocessing.Process(target=speakingProcessFunction, args=(game.GetSpeakingQueue(), game.GetGameStep()))
    speakingProcess.start()

    while True:
        STR.Update()
        game.Update()
