from Settingator import *
from PySerialCommunicator import *
from PySimpleGUIDisplay import *
#from DearPyGUIDisplay import *
import csv
import random
import time
import multiprocessing
import pyttsx3
import pygame.mixer as mx
import openai
import sys
import gc
from TKDisplay import *


com:SerialCTR

display:TKDisplay

STR:Settingator

###   GAME SYSTEM    ###

NUMBER_PLAYER = 4
QUESTION_FILENAME = "question.csv"
TESTING = True

GS_INIT = 0
GS_WAITING_TO_START = 1
GS_ABOUT_TO_READ = 2
GS_READING = 3
GS_WAITING = 4
GS_REWARDING = 5
GS_FINISHED = 6
GS_FINISHED_READING = 7
GS_FINISHED_REWARDING = 8
GS_INTRODUCING = 9
GS_SPEAKING = 10

RED_BUTTON = 13
GREEN_BUTTON = 12
YELLOW_BUTTON = 14
BLUE_BUTTON = 27

class Player():
    def __init__(self):
        self.__score = 0
        self.__good = 0
        self.__bonus = 0
        self.__bad = 0
        self.__slave = None
        self.__order = 0
        self.__answeredCurrentQuestion = False
        self.__lastAnswer = None
        self.__name = "non défini"
        self.__position = 5.0
        self.__positionElement:LayoutElement
        self.__goodElement:LayoutElement
        self.__badElement:LayoutElement
        self.__playerLayout:LayoutElement = None

    def __del__(self):
        pass

    def CreateLayout(self) -> None:
        frameName:str = "Player " + str(self.__order) + " : Slave " + str(self.GetSlave().GetID())

        self.__positionElement = LayoutElement(IDP_INPUT, self.GetPosition(), "Target Position", callback=lambda value : self.SetPosition(value))
        self.__goodElement = LayoutElement(IDP_TEXT, "Good: " + str(self.__good))
        self.__badElement = LayoutElement(IDP_TEXT, "Bad: " + str(self.__bad))

        self.__playerLayout = LayoutElement(IDP_COLUMN, None, frameName, [
                                                        LayoutElement(IDP_BUTTON, None, "target", callback=lambda value : targetPlayer(self.GetOrder())),
                                                        LayoutElement(IDP_TEXT, "Player Name"),
                                                        LayoutElement(IDP_INPUT, self.GetName(), "Player Name", callback=lambda value : self.SetName(value)),
                                                        LayoutElement(IDP_TEXT, "Target Position :"),
                                                        self.__positionElement,
                                                        self.__goodElement,
                                                        self.__badElement
                                                    ])
        STR.AddToLayout(self.__playerLayout)
                                                
    def GetLayout(self) -> LayoutElement:
        return self.__playerLayout

    def GetName(self):
        return self.__name
    
    def SetName(self, name):
        self.__name = name

    def GetPosition(self) -> float:
        return self.__position
    
    def SetPosition(self, position):
        if position == '':
            position = 0
        self.__position = float(position)

    def SetSlave(self, slave:Slave):
        self.__slave = slave

    def Send(self, settingName:str):
        if isinstance(self.__slave, Slave):
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
        self.__good += 1
        self.UpdateScore()
    
    def IncreaseFail(self):
        self.__bad += 1
        self.UpdateScore()

    def ResetScore(self):
        self.SetScore(0, 0)

    def UpdateScore(self):
        self.__score = self.__good - self.__bad

        if self.__goodElement != None:
            self.__goodElement.UpdateValue("Good: " + str(self.__good))

        if self.__badElement != None:
            self.__badElement.UpdateValue("Bad: " + str(self.__bad))

    def GetScore(self):
        return self.__score
    
    def GetGood(self):
        return self.__good
    
    def GetBad(self):
        return self.__bad
    
    def SetScore(self, good, bad):
        self.__good = good
        self.__bad = bad
        self.UpdateScore()

    def GetFrameElement(self):
        return self.__frameElement
    
    def SetFrameBGColor(self, color):
        self.__playerLayout.GetIElement().SetBGColor(color)

    def GetNameElement(self):
        return self.__nameElement
    
    def GetPositionElement(self):
        return self.__positionElement
    
    def ReWriteName(self):
        if (self.__nameElement()):
            self.__nameElement.GetValue().UpdateValue(self.__name)

    def ReWritePosition(self):
        if (self.__positionElement()):
            self.__positionElement.GetValue().UpdateValue(self.__position)

    def GetGoodText(self):
        return self.__goodText
    
    def GetBadText(self):
        return self.__badText
    
    def PrepareToDestroy(self) -> None:
        self.__layout = None
        self.__nameElement = None
        self.__positionElement = None
        self.__frameElement = None
        self.__goodText = None
        self.__badText = None


class Players(IRefreshable):
    def __init__(self):
        self.__playerList = dict()
        self.__nbPlayers = 0
        self.__orderedPlayerList = dict()
        self.__numberOrderedPlayer = 0

    def AddPlayer(self, slave:Slave):
        print("Adding a player")
        newPlayer = Player()
        print("player created");
        newPlayer.SetSlave(slave)
        newPlayer.Send("GREEN LOADING")
        print("Green loading sended")
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
        if player:
            self.__numberOrderedPlayer += 1
            self.__orderedPlayerList[self.__numberOrderedPlayer] = player
            player.Send("GREEN GOOD")
            player.SetOrder(self.__numberOrderedPlayer)
            player.CreateLayout()
            #display.UpdateLayout(STR.GetSlaveSettings())

    def IsOrderedPlayer(self, slaveID:int) -> bool:
        player = self.GetPlayerBySlaveID(slaveID)

        if player in self.__orderedPlayerList.values():
            return True
        return False

    def GetNumberOfOrderedPlayer(self):
        return self.__numberOrderedPlayer

    def AllAnswered(self):
        allAnswered = True

        for player in self.__playerList:
            if self.__playerList[player].CanAnswer():
                allAnswered = False

        if self.__playerList.__len__() == 0:
            allAnswered = False

        return allAnswered
    
    def SendAll(self, command):
        for player in self.__playerList:
            self.__playerList[player].Send(command)

    def GetList(self):
        return self.__playerList
    
    def SetAllBGColor(self, color):

        for player in self.__playerList:
            self.__playerList[player].SetFrameBGColor(color)

    def ReWriteName(self):

        for player in self.__playerList:
            self.__playerList[player].ReWriteName()

    def ReWritePosition(self):

        for player in self.__playerList:
            self.__playerList[player].ReWritePosition()

    def ResetScore(self):
        for player in self.__playerList:
            self.__playerList[player].ResetScore()

    def UpdateAllScore(self):
        for player in self.__playerList:
            self.__playerList[player].UpdateScore()

    def RefreshElementDisplay(self) -> None:
        self.UpdateAllScore()
        self.ReWriteName()
        self.ReWritePosition()

    def ResetPlayer(self) -> None:
        for player in self.__playerList:
            self.__playerList[player].Send("GREEN LOADING")
            display.RemoveLayout(self.__playerList[player].GetLayout())
            self.__playerList[player].PrepareToDestroy()

        self.__orderedPlayerList.clear()
        self.__nbPlayers = 0
        self.__playerList.clear()
        display.UpdateLayout()
        gc.collect()

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
                player.SetFrameBGColor(RED_COLOR)

            elif button == GREEN_BUTTON:                
                player.SetLastAnswer(1)
                player.SetFrameBGColor(GREEN_COLOR)

            elif button == YELLOW_BUTTON:
                player.SetLastAnswer(2)
                player.SetFrameBGColor(YELLOW_COLOR)

            elif button == BLUE_BUTTON:
                player.SetLastAnswer(3)
                player.SetFrameBGColor(BLUE_COLOR)

            display.Update()
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
DEFAULT_BG_COLOR = "#64778D"

class AIVoice():
    def __init__(self):
        api_key = ""
        with open("openai_api_key.txt") as apiKeyFile:
            api_key = apiKeyFile.read()

        self.__openai = openai.OpenAI(api_key=api_key)

        self.__preprompt = ""
        with open("openai_preprompt.txt", encoding="utf-8") as prepromptFile:
            self.__preprompt = prepromptFile.read()
        self.__memory = []
        self.__model = "gpt-4o-mini"

    def MakeRequest(self, content:str) -> str:
        messages = []
        messages.append({"role": "system", "content": self.__preprompt})

        for msg in self.__memory:
            messages.append({"role": "assistant", "content": msg})

        messages.append({"role": "user", "content": content})

        completion = self.__openai.chat.completions.create(model=self.__model, messages=messages)

        self.__memory.append(content)
        self.__memory.append(completion.choices[0].message.content)

        return completion.choices[0].message.content

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

        self.__ansFrame = ansAFrame

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

        self.__labelWidth = int(self.__screenWidth/1)
        self.__labelHeight = int(self.__screenHeight/4 - 20)

        length = sg.Text.string_width_in_pixels("_ 3000", "WWWWWWWWWWWWWWW")
        
        width = int(self.__labelWidth * 2.0/3.0)
        fontSize = int(3000 * (width / length))

        nameFont = "_ " + str(fontSize)
        scoreFont = "Inconsolata " + str(fontSize)

        scoreLayout = []
        
        self.__playersElements = []

        for index in range(0, NUMBER_PLAYER):
            playerElements = dict()

            playerElements['name'] = self.__newPlayerName(self.__colorFromIndex(index), nameFont)
            playerElements['good'] = self.__newPlayerScore(self.__colorFromIndex(index), GREEN_COLOR, scoreFont)
            playerElements['bad'] = self.__newPlayerScore(self.__colorFromIndex(index), RED_COLOR, scoreFont)
            playerElements['total'] = self.__newPlayerScore(self.__colorFromIndex(index), YELLOW_COLOR, scoreFont)

            scoreLayout.append([self.__newPlayerFrame(self.__colorFromIndex(index),
                                                      playerElements['name'],
                                                      playerElements['good'],
                                                      playerElements['bad'],
                                                      playerElements['total'])])
            
            self.__playersElements.append(playerElements)

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

    def __colorFromIndex(self, index):
        if index == 0:
            return GOLD_COLOR
        if index == 1:
            return SILVER_COLOR
        if index == 2:
            return BRONZE_COLOR
        if index == 3:
            return DARK_RED_COLOR

    def Update(self):
        event, values = self.__PSGWindow.read(0)
        if event == 'Escape:27':
            self.__PSGWindow.Close()
            #display.Close()

        if callable(event):
            event()

    def SetQuestion(self, question:str, ansA:str, ansB:str, ansC:str, ansD:str):

        self.__scoreDisplayFrame.update(visible=False)
        self.__questionDisplayFrame.update(visible=True)
        self.__PSGWindow.read(0)

        part1 = ""
        part2 = ""

        questionCharLen = question.__len__()
        questionCharMid = int(questionCharLen / 2)

        for offset in range(0, questionCharMid):
            if question[questionCharMid + offset] == ' ':
                question = question[:questionCharMid + offset] + '\n' + question[questionCharMid + offset + 1:]
                part1 = question[:questionCharMid + offset]
                part2 = question[questionCharMid - offset + 1:]
                print("+ offset")
                break
            
            elif question[questionCharMid - offset] == ' ':
                question = question[:questionCharMid - offset] + '\n' + question[questionCharMid - offset + 1:]
                part1 = question[:questionCharMid + offset]
                part2 = question[questionCharMid - offset + 1:]
                print("- offset")
                break

        print(question)
        
        part1Length = sg.Text.string_width_in_pixels("_ 3000", part1)
        part2Length = sg.Text.string_width_in_pixels("_ 3000", part2)

        questionLength = part1Length if part1Length > part2Length else part2Length

        width = self.__screenWidth - 80
        fontSize = int(3000 * (width / questionLength))
        fontStr = "_ "+str(fontSize)
        print(fontStr)

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

        height = sg.Text.char_height_in_pixels(fontStr)

        ansFrameWidth, ansFrameHeight = self.__ansFrame.get_size()

        ansFrameHeight = ansFrameHeight - 20

        if height > ansFrameHeight:
            fontSize = int(fontSize * (ansFrameHeight / height))
        fontStr = "_ "+str(fontSize)

        self.__ansAText.update(value=ansA, font=fontStr)
        self.__ansBText.update(value=ansB, font=fontStr)
        self.__ansCText.update(value=ansC, font=fontStr)
        self.__ansDText.update(value=ansD, font=fontStr)

    def SetScore(self, orderedPlayers):

        for index in range(0, NUMBER_PLAYER):
            self.__playersElements[index]['name'].update(orderedPlayers[index].GetName())
            self.__transformAndUpdate(orderedPlayers[index].GetGood(), self.__playersElements[index]['good'])
            self.__transformAndUpdate(orderedPlayers[index].GetBad(), self.__playersElements[index]['bad'])
            self.__transformAndUpdate(orderedPlayers[index].GetScore(), self.__playersElements[index]['total'])

        self.__questionDisplayFrame.update(visible=False)
        self.__scoreDisplayFrame.update(visible=True)

        self.__PSGWindow.read(0)

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

    def Close(self):
        self.__PSGWindow.Close()

class Game():
    def __init__(self):
        self.__questionPool = []
        self.__question = 0
        self.__mode = NULL
        self.__speakingQueue = multiprocessing.Queue()
        self.__gameStepLock = multiprocessing.Lock()
        self.__gameStep = multiprocessing.Value('i', GS_INIT)
        self.__isSpeaking = multiprocessing.Value('i', False)
        self.__finishedReadingTimestamp = 0
        self.__currentQuestionGoodAnswer = 0
        self.__accelDone = False
        #self.__questionAndScoreDisplay = QuestionAndScoreDisplay()
        #display.AddStuffToClose(self.__questionAndScoreDisplay)
        self.__aiVoice = AIVoice()
        self.__nextStepAfterSpeak = 0
        self.__isRunning = True

        ### Sound Management ###
        mx.init(channels=1)
        self.__channel = mx.Channel(0)
        self.__goodSound = mx.Sound("good.wav")
        self.__badSound = mx.Sound("bad.wav")
        self.__waitingSound = mx.Sound("waiting.wav")
        self.__endWaitSound = mx.Sound("endWait.wav")
        self.__countdownSound = mx.Sound("shotCountdown2.wav")
        self.__aimingSound = mx.Sound("aiming2.wav")

    def isRunning(self):
        return self.__isRunning

    def MakeAIVoiceRequest(self, request:str):
        return self.__aiVoice.MakeRequest(request)

    def PlayAimingSound(self):
        self.__channel.play(self.__aimingSound, -1)

    def PlayCountdownSound(self):
        self.__channel.play(self.__countdownSound)

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

        ControlColumnLayout.RemoveElement(startGameAutoButton)
        ControlColumnLayout.RemoveElement(startGameManualButton)
        display.UpdateLayout()

        allQuestion = []
        
        with open(QUESTION_FILENAME, encoding="utf-8") as questionFile:
            csvContent = csv.reader(questionFile, delimiter=';')

            for row in csvContent:
                allQuestion.append(row)

        random.seed(time.time())
        numberQuestion = allQuestion.__len__()

        for index in range(1, numberQuestion, 1):
            questionNo = random.randint(0, allQuestion.__len__() - 1)
            self.__questionPool.append(allQuestion[questionNo])
            allQuestion.remove(allQuestion[questionNo])

        self.__gameStep.value = GS_INTRODUCING

        playerListString = ""

        for index in range(1, NUMBER_PLAYER + 1):
            playerListString += playerList.GetPlayerByOrder(index).GetName() + " "

        self.Say(self.__aiVoice.MakeRequest("Présentation: les joueurs sont " + playerListString))

    def Update(self):
        if self.__mode == AUTO:
            if self.__gameStep.value == GS_ABOUT_TO_READ:

                if self.__question < self.__questionPool.__len__():
                    playerList.SendAll("BLUE LOADING")
                    playerList.SetAllBGColor(DEFAULT_BG_COLOR)
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

                    
                    self.__questionAndScoreDisplay.SetQuestion(question[1], question[answerOrder[0]], question[answerOrder[1]], question[answerOrder[2]], question[answerOrder[3]])
                    questionStr = question[1] + " Réponse A: " + question[answerOrder[0]] + ", Réponse B: " + question[answerOrder[1]] + ", Réponse C: " + question[answerOrder[2]] + ", Réponse D: " + question[answerOrder[3]] + " ?"
                    self.Ask(questionStr)
                    self.__gameStep.value = GS_READING
                
                else:
                    self.Say("Il n'y a plus de questions")
                    self.__gameStep.value = GS_SPEAKING
                    self.__nextStepAfterSpeak = GS_INIT

            elif self.__gameStep.value == GS_READING:
                if self.__isSpeaking.value == False:
                    self.__gameStep.value = GS_FINISHED_READING

            elif self.__gameStep.value == GS_FINISHED_READING:
                self.PlayWaitingSound()
                print("finishedReading")

                self.__gameStep.value = GS_WAITING
                self.__finishedReadingTimestamp = time.time()
                self.__accelDone = False

                if TESTING:
                    self.__finishedReadingTimestamp -= 10

            elif self.__gameStep.value == GS_WAITING:
                if time.time() - self.__finishedReadingTimestamp >= 10 or playerList.AllAnswered():
                    self.PlayEndWaitSound()
                    playerList.SendAll("BLUE FROZEN")
                    time.sleep(1)
                    print("starting rewarding")

                    if TESTING:
                        self.__gameStep.value = GS_REWARDING
                    else:
                        self.__gameStep.value = GS_REWARDING
                
                elif not self.__accelDone and time.time() - self.__finishedReadingTimestamp >= 7 and not TESTING:
                    for playerIndex in range(1, NUMBER_PLAYER + 1):
                        player:Player = playerList.GetPlayerByOrder(playerIndex)

                        if player.CanAnswer():
                            player.Send("RED ACCEL LOADING")

                    self.__accelDone = True

            elif self.__gameStep.value == GS_REWARDING:
                if target.Reward(self.__currentQuestionGoodAnswer):
                    self.Say("La bonne réponse était: " + self.__questionPool[self.__question][2])

                    self.__gameStep.value = GS_SPEAKING
                    self.__nextStepAfterSpeak = GS_FINISHED_REWARDING

            elif self.__gameStep.value == GS_FINISHED_REWARDING:
                time.sleep(3)

                if not TESTING:
                    for playerIndex in range(1, NUMBER_PLAYER + 1):
                        playerList.GetPlayerByOrder(playerIndex).ResetAnswered()

                if  (self.__question + 4) % 6 == 0:
                    self.__scoreAnnounce(playerList)
                    self.__gameStep.value = GS_SPEAKING
                    self.__nextStepAfterSpeak = GS_ABOUT_TO_READ
                else:
                    self.__gameStep.value = GS_ABOUT_TO_READ

                if (self.__question + 1) % 6 == 0:
                    self.__scoreAnnounce(playerList, True)
                    self.__gameStep.value = GS_SPEAKING
                    self.__nextStepAfterSpeak = GS_FINISHED
                
                self.__question += 1

            elif self.__gameStep.value == GS_FINISHED:
                ControlColumnLayout.AppendElement(NouvelleMancheButton)
                display.UpdateLayout()

                self.__gameStep.value = GS_INIT
            
            elif self.__gameStep.value == GS_INTRODUCING:
                if self.__isSpeaking.value == False:
                    self.__gameStep.value = GS_ABOUT_TO_READ

            elif self.__gameStep.value == GS_SPEAKING:
                if self.__isSpeaking.value == False:
                    self.__gameStep.value = self.__nextStepAfterSpeak

        elif self.__mode == MANUAL:
            pass

        #self.__questionAndScoreDisplay.Update()

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

    def GetIsSpeaking(self):
        return self.__isSpeaking
    
    def GetIsSpeakingValue(self):
        return self.__isSpeaking.value

    def Ask(self, sentence:str):
        self._Speak(sentence, True)

    def Say(self, sentence:str, wait:bool = True):
        self._Speak(sentence, False)

    def CanAnswer(self):
        gameStep = self.GetGameStepValue()

        return (gameStep == GS_READING or gameStep == GS_FINISHED_READING or gameStep == GS_WAITING)

    def _Speak(self, sentence:str, isQuestion:bool = True):
        self.__isSpeaking.value = True
        self.__speakingQueue.put((sentence, isQuestion))

    def SetScoreDisplay(self, orderedPlayers):
        self.__questionAndScoreDisplay.SetScore(orderedPlayers)

    def TestScoreAnnounce(self):
        self.__scoreAnnounce(playerList)

    def SetQuestionDisplay(self, question, ansA, ansB, ansC, ansD):
        self.__questionAndScoreDisplay.SetQuestion(question, ansA, ansB, ansC, ansD)

    def __scoreAnnounce(self, playerList:Players, final:bool = False):
        unorderedPlayers = []

        requestString = ""
        if final:
            requestString = "Score Final: "
            self.__nextStepAfterSpeak = GS_ABOUT_TO_READ
        else:
            requestString = "Score: "
            self.__nextStepAfterSpeak = GS_INIT

        for index in range(0, NUMBER_PLAYER):
            thePlayer:Player = playerList.GetPlayer(index)
            unorderedPlayers.append(thePlayer)

        orderedPlayers = []

        for index in range(0, NUMBER_PLAYER):
            highestScore = -100
            highestScoreIndex = 0

            for secondIndex in range(0, unorderedPlayers.__len__()):
                if highestScore < unorderedPlayers[secondIndex].GetScore():
                    highestScore = unorderedPlayers[secondIndex].GetScore()
                    highestScoreIndex = secondIndex

            orderedPlayers.append(unorderedPlayers[highestScoreIndex])

            requestString += unorderedPlayers[highestScoreIndex].GetName() +\
                    ": bonnes réponses: " + str(unorderedPlayers[highestScoreIndex].GetGood()) +\
                    " mauvaises réponses: " + str(unorderedPlayers[highestScoreIndex].GetBad()) +\
                    " total: " + str(unorderedPlayers[highestScoreIndex].GetScore()) + ". "

            unorderedPlayers.remove(unorderedPlayers[highestScoreIndex])

        annoucementString = self.__aiVoice.MakeRequest(requestString)

        self.SetScoreDisplay(orderedPlayers)
        self.Say(annoucementString)
        
        self.__gameStep.value = GS_SPEAKING

    def SetNextStepAfterSpeak(self, step):
        self.__nextStepAfterSpeak = step


game:Game          
        
########################


### TARGETING SYSTEM ###

TP_START = 0.0
TP_END = 180.0

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
        self.__currentRewardingPlayerIncrementation = +1
        self.__kiddingSentence = ""
        self.__randomKidding = False
        self.__shouldKidding = False
        self.__firstRewardCall = True

    def Reward(self, goodAnswer:int) -> bool:
        if self.__firstRewardCall:
            self.__firstRewardCall = False

            if self.__turretPos >= NUMBER_PLAYER / 2:
                self.__currentRewardingPlayerIncrementation = -1
                self.__currentRewardingPlayer = NUMBER_PLAYER - 1

            else:
                self.__currentRewardingPlayerIncrementation = +1
                self.__currentRewardingPlayer = 0

        if not self.__allRewarded:
            if TESTING and self.__targetDone == False:
                self.__targetDone = True
                self.__targetDoneTimestamp = time.time()

            if not self.__targetDone and not self.__targetting:
                targetPlayer(None, self.__currentRewardingPlayer+1)
                game.PlayAimingSound()

            if self.__targetDone:
                if self.__randomKidding == False:
                    game.PlayCountdownSound()

                    self.__randomKidding = True

                    if random.randint(0, 2999) % 3 == 0:
                        self.__shouldKidding = True
                        playerToReward:Player = playerList.GetPlayerByOrder(self.__currentRewardingPlayer+1)
                        shoot = playerToReward.GetLastAnswer() != goodAnswer

                        requestString = "Récompense: " + playerToReward.GetName() + " "
                        if shoot:
                            requestString += "se fait tirer dessus."
                        else:
                            requestString += "ne se fait pas tirer dessus."

                        self.__kiddingSentence = game.MakeAIVoiceRequest(requestString)


                if time.time() - self.__targetDoneTimestamp > 2:
                    playerToReward:Player = playerList.GetPlayerByOrder(self.__currentRewardingPlayer+1)
                    shoot = playerToReward.GetLastAnswer() != goodAnswer

                    if not shoot:
                        playerToReward.IncreaseGood()
                        playerToReward.Send("GREEN GOOD")
                        game.PlayGoodSound()
                    else:
                        playerToReward.IncreaseFail()
                        playerToReward.Send("RED BAD")
                        if not TESTING:
                            turret.SendSettingUpdateByName("SHOOT")
 
                        game.PlayBadSound()
                    
                    time.sleep(1)

                    if self.__shouldKidding:
                        game.Say(self.__kiddingSentence)
                        game.SetGameStep(GS_SPEAKING)
                        game.SetNextStepAfterSpeak(GS_REWARDING)

                    self.__kiddingSentence = ""
                    self.__shouldKidding = False
                    self.__randomKidding = False

                    self.__currentRewardingPlayer += self.__currentRewardingPlayerIncrementation
                    self.__targetDone = False

                    if self.__currentRewardingPlayer == NUMBER_PLAYER or self.__currentRewardingPlayer == -1:
                        self.__allRewarded = True

        else:
            self.__allRewarded = False


        if self.__allRewarded:
            self.__firstRewardCall = True

        return self.__allRewarded

    def TargetPlayer(self, orderedPlayer:int):
        global turret
        self.__targetedPlayer = playerList.GetPlayerByOrder(orderedPlayer)

        distance = abs(self.__targetedPlayer.GetPosition() - self.__turretPos)

        time = distance / 5.0
        turret.SendSettingUpdateByName("UInt32", int(time * 1000) )
        turret.SendSettingUpdateByName("CUSTOM FLOAT", self.__targetedPlayer.GetPosition())
        self.__turretPos = self.__targetedPlayer.GetPosition()

    def SetTurretPos(self, turretPos):
        self.__turretPos = turretPos

target = Target()

def targetPlayer(orderedPlayer:int):
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

def startGameAuto(value):
    game.Start(AUTO)

startGameAutoButton = LayoutElement(IDP_BUTTON, None, "startGameAuto", callback=startGameAuto)

def startGameManual(wvalue):
    game.Start(MANUAL)

startGameManualButton = LayoutElement(IDP_BUTTON, None, "startGameManual", callback=startGameManual)

def initPlayer(value):
    STR.AddNotifCallback(RED_BUTTON, initNotifLaser)

InitPlayerButton = LayoutElement(IDP_BUTTON, None, "initPlayer", callback=initPlayer)

def nouvelleManche(value):
    ControlColumnLayout.RemoveElement(NouvelleMancheButton)
    display.UpdateLayout()
    game.SetGameStep(GS_ABOUT_TO_READ)

NouvelleMancheButton = LayoutElement(IDP_BUTTON, None, "Nouvelle Manche", callback=nouvelleManche)

#TEST#

def testDisplayQuestion(value):
    game.SetQuestionDisplay("Combien de fois par seconde un colibri peut-il battre des ailes ?", "La réponse A", "La grosse réponse B", "repC", "Et non pas la D")

testDisplayQuestionButton = LayoutElement(IDP_BUTTON, None, "testDisplayQuestion", callback=testDisplayQuestion)

def testDisplayScore(value):
    game.TestScoreAnnounce()

testDisplayScoreButton = LayoutElement(IDP_BUTTON, None, "testDisplayScore", callback=testDisplayScore)

######

def initNotifLaser(slaveID:int):
    if playerList.IsOrderedPlayer(slaveID):
        return
    playerList.AddOrderedPlayer(playerList.GetPlayerBySlaveID(slaveID))

    if playerList.GetNumberOfOrderedPlayer() >= NUMBER_PLAYER:
        STR.RemoveNotifCallback(RED_BUTTON)
        ControlColumnLayout.RemoveElement(InitPlayerButton)
        global turretPos
        global gameStep

        target.SetTurretPos(TP_END)
        ControlColumnLayout.AppendElement(startGameAutoButton)
        ControlColumnLayout.AppendElement(startGameManualButton)
        game.SetGameStep(GS_WAITING_TO_START)
        display.UpdateLayout()

        STR.AddNotifCallback(RED_BUTTON, lambda slaveID : playerPressButton(slaveID, RED_BUTTON))
        STR.AddNotifCallback(GREEN_BUTTON, lambda slaveID : playerPressButton(slaveID, GREEN_BUTTON))
        STR.AddNotifCallback(BLUE_BUTTON, lambda slaveID : playerPressButton(slaveID, BLUE_BUTTON))
        STR.AddNotifCallback(YELLOW_BUTTON, lambda slaveID : playerPressButton(slaveID, YELLOW_BUTTON))

########################

### SPEAKING PROCESS ###

def speakingProcessFunction(queue:multiprocessing.Queue, gameStep, speaking, shouldRun):
    engine = pyttsx3.init()
    engine.setProperty('volume', 1)

    voices = engine.getProperty('voices')

    for voice in voices:
        if "French" in voice.name:
            engine.setProperty("voice", voice.id)
            break

    while shouldRun.value:
        sentence, isQuestion = queue.get()
        engine.say(sentence)
        speaking.value = True
        engine.runAndWait()
        speaking.value = False

########################

def DeskCallback(slave:Slave):
    playerList.AddPlayer(slave)

def TurretCallback(slave:Slave):
    global turret
    turret = slave

####### TESTING ########

def CreateDummyPlayers():
    playerList.AddPlayer(Slave(STR, 0, dict()))
    playerList.AddOrderedPlayer(playerList.GetPlayer(0))
    playerList.GetPlayer(0).SetScore(0, 3)

    playerList.AddPlayer(Slave(STR, 1, dict()))
    playerList.AddOrderedPlayer(playerList.GetPlayer(1))
    playerList.GetPlayer(1).SetScore(2, 1)

    playerList.AddPlayer(Slave(STR, 2, dict()))
    playerList.AddOrderedPlayer(playerList.GetPlayer(2))
    playerList.GetPlayer(2).SetScore(3, 0)

    playerList.AddPlayer(Slave(STR, 3, dict()))
    playerList.AddOrderedPlayer(playerList.GetPlayer(3))
    playerList.GetPlayer(3).SetScore(1, 2)

def testButtonColor(value):
    playerPressButton(0, RED_BUTTON)
    playerPressButton(1, GREEN_BUTTON)
    playerPressButton(2, BLUE_BUTTON)
    playerPressButton(3, YELLOW_BUTTON)
    display.Update()

########################

if __name__ == "__main__":
    com = SerialCTR(PySimpleGUIDisplay.SelectCOMPort(SerialCTR))

    #display = DearPyGUIDisplay()
    #display = PySimpleGUIDisplay()
    display = TKDisplay()
    #display.AddElementToRefresh(playerList)

    STR = Settingator(com, display)

    STR.AddNotifCallback(RED_BUTTON, lambda slaveID : playerPressButton(slaveID, RED_BUTTON))
    STR.AddNotifCallback(GREEN_BUTTON, lambda slaveID : playerPressButton(slaveID, GREEN_BUTTON))
    STR.AddNotifCallback(BLUE_BUTTON, lambda slaveID : playerPressButton(slaveID, BLUE_BUTTON))
    STR.AddNotifCallback(YELLOW_BUTTON, lambda slaveID : playerPressButton(slaveID, YELLOW_BUTTON))

    STR.AddNotifCallback(LASER_NOTIF, notifLaser)
    STR.SendBridgeInitRequest(1, b'Turret', TurretCallback)
    STR.SendBridgeInitRequest(2, b'Desk', DeskCallback, NUMBER_PLAYER)

    ControlColumnLayout = LayoutElement(IDP_COLUMN)

    ControlColumnLayout.AppendElement(InitPlayerButton)
    ControlColumnLayout = LayoutElement(IDP_COLUMN)

    ControlColumnLayout.AppendElement(InitPlayerButton)
    ControlColumnLayout = LayoutElement(IDP_COLUMN)

    ControlColumnLayout.AppendElement(InitPlayerButton)
    if TESTING:
        ControlColumnLayout.AppendElement(startGameAutoButton)
        ControlColumnLayout.AppendElement(startGameManualButton)
        pass

    ControlColumnLayout.AppendElement(testDisplayQuestionButton)
    ControlColumnLayout.AppendElement(testDisplayScoreButton)

    if TESTING:
        ControlColumnLayout.AppendElement(LayoutElement(IDP_BUTTON, None, "test button Color", callback=testButtonColor))

    if TESTING:
        TestBugButton = LayoutElement(IDP_BUTTON, None, "Test Bug", callback=lambda value : print(gc.get_referrers(playerList.GetPlayer(0))))
        ControlColumnLayout.AppendElement(TestBugButton)

        AimingSoundButton = LayoutElement(IDP_BUTTON, None, "aiming", callback=lambda value : game.PlayAimingSound())
        CountdownSoundButton = LayoutElement(IDP_BUTTON, None, "countdown", callback=lambda value : game.PlayCountdownSound())

        ControlColumnLayout.AppendElement(AimingSoundButton)
        ControlColumnLayout.AppendElement(CountdownSoundButton)
                                                


    ControlColumnLayout.AppendElement(LayoutElement(IDP_BUTTON, None, "Reset Score", callback=lambda value : playerList.ResetScore()))

    ControlColumnLayout.AppendElement(LayoutElement(IDP_BUTTON, None, "Reset Player", callback=lambda value : playerList.ResetPlayer()))

    if TESTING:
        ControlColumnLayout.AppendElement(LayoutElement(IDP_BUTTON, None, "Test BG", callback=lambda value : playerList.SetAllBGColor(RED_COLOR)))

    STR.AddToLayout(ControlColumnLayout)
    
    game = Game()


    shouldRun = multiprocessing.Value('i', True)
    speakingProcess = multiprocessing.Process(target=speakingProcessFunction, args=(game.GetSpeakingQueue(), game.GetGameStep(), game.GetIsSpeaking(), shouldRun))
    speakingProcess.start()

    if TESTING:
        CreateDummyPlayers()
        
        
    STR.SendInitRequest(1)
    #STR.SendBridgeInitRequest(1, b'Turret', TurretCallback)
    #STR.SendBridgeInitRequest(2, b'Desk', DeskCallback, NUMBER_PLAYER)

    #STR.SendInitRequest(1)
    STR.SendBridgeInitRequest(1, b'Turret', TurretCallback)
    STR.SendBridgeInitRequest(2, b'Desk', DeskCallback, NUMBER_PLAYER)

    while display.IsRunning():
        STR.Update()
        game.Update()

    shouldRun.value = False
    speakingProcess.terminate()
    
    #dpg.destroy_context()
