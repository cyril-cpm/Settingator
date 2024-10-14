import PySimpleGUI as sg

RED_COLOR = "#FF0000"
BLUE_COLOR = "#0000FF"
GREEN_COLOR = "#00FF00"
YELLOW_COLOR = "#FFFF00"
DARK_GREY_COLOR = "#222222"
BLACK_COLOR = "#000000"
LIGHT_GREY_COLOR = "#666666"
GOLD_COLOR = "#D3AF37"
SILVER_COLOR = "#A8A9AD"
BRONZE_COLOR = "#49371B"

class QuestionDisplay():
    def __init__(self):

        self.__PSGLayout = [[]]
        x, y =sg.Window.get_screen_size()

        #### QUESTION DISPLAY ####

        questionDisplayLayout = [[],[]]

        self.__questionText = sg.Text("", background_color=DARK_GREY_COLOR, expand_x=True, justification="center")
        questionFrameLayout = [[sg.VPush(background_color=DARK_GREY_COLOR)], [self.__questionText], [sg.VPush(background_color=DARK_GREY_COLOR)]]
        questionFrame = sg.Frame("", questionFrameLayout, border_width=0, background_color=DARK_GREY_COLOR, expand_y=True, pad=10, size=(x- 20, 1))

        self.__ansAText = sg.Text("", background_color=RED_COLOR, expand_x=True, justification="center")
        self.__ansBText = sg.Text("", background_color=GREEN_COLOR, expand_x=True, justification="center")
        self.__ansCText = sg.Text("", background_color=YELLOW_COLOR, expand_x=True, justification="center")
        self.__ansDText = sg.Text("", background_color=BLUE_COLOR, expand_x=True, justification="center")

        ansAFrame = sg.Frame("", [[sg.VPush(background_color=RED_COLOR)], [self.__ansAText], [sg.VPush(background_color=RED_COLOR)]], border_width=0, background_color=RED_COLOR, size=(int(x/2) - 20,1), expand_y=True, pad=10)
        ansBFrame = sg.Frame("", [[sg.VPush(background_color=GREEN_COLOR)], [self.__ansBText], [sg.VPush(background_color=GREEN_COLOR)]], border_width=0, background_color=GREEN_COLOR, size=(int(x/2) - 20,1), expand_y=True, pad=10)
        ansCFrame = sg.Frame("", [[sg.VPush(background_color=YELLOW_COLOR)], [self.__ansCText], [sg.VPush(background_color=YELLOW_COLOR)]], border_width=0, background_color=YELLOW_COLOR, size=(int(x/2) - 20,1), expand_y=True, pad=10)
        ansDFrame = sg.Frame("", [[sg.VPush(background_color=BLUE_COLOR)], [self.__ansDText], [sg.VPush(background_color=BLUE_COLOR)]], border_width=0, background_color=BLUE_COLOR, size=(int(x/2) - 20,1), expand_y=True, pad=10)

        answerFrameLayout = [[],[]]
        answerFrameLayout[0].append(ansAFrame)
        answerFrameLayout[0].append(ansBFrame)
        answerFrameLayout[1].append(ansCFrame)
        answerFrameLayout[1].append(ansDFrame)

        answerFrame = sg.Frame("", answerFrameLayout, border_width=0, background_color=LIGHT_GREY_COLOR, size=(x - 20,1), expand_y=True, pad=10)

        questionDisplayLayout[0].append(questionFrame)
        questionDisplayLayout[1].append(answerFrame)
        self.__questionDisplayFrame = sg.Column(questionDisplayLayout, expand_x=True, expand_y=True, background_color=BLACK_COLOR, pad=0, visible=False)

        self.__PSGLayout[0].append(self.__questionDisplayFrame)

        ########################

        #### SCORE DISPLAY #####

        self.__firstPlayerName = sg.Text("", background_color=GOLD_COLOR)
        self.__secondPlayerName = sg.Text("", background_color=SILVER_COLOR)
        self.__thirdPlayerName = sg.Text("", background_color=BRONZE_COLOR)
        self.__fourthPlayerName = sg.Text("", background_color=RED_COLOR)

        self.__firstPlayerGood = sg.Text("", background_color=GOLD_COLOR, text_color=GREEN_COLOR)
        self.__secondPlayerGood = sg.Text("", background_color=SILVER_COLOR, text_color=GREEN_COLOR)
        self.__thirdPlayerGood = sg.Text("", background_color=BRONZE_COLOR, text_color=GREEN_COLOR)
        self.__fourthPlayerGood = sg.Text("", background_color=RED_COLOR, text_color=GREEN_COLOR)

        self.__firstPlayerBad = sg.Text("", background_color=GOLD_COLOR, text_color=RED_COLOR)
        self.__secondPlayerBad = sg.Text("", background_color=SILVER_COLOR, text_color=RED_COLOR)
        self.__thirdPlayerBad = sg.Text("", background_color=BRONZE_COLOR, text_color=RED_COLOR)
        self.__fourthPlayerBad = sg.Text("", background_color=RED_COLOR, text_color=RED_COLOR)

        self.__firstPlayerTotal = sg.Text("", background_color=GOLD_COLOR, text_color=YELLOW_COLOR)
        self.__secondPlayerTotal = sg.Text("", background_color=SILVER_COLOR, text_color=YELLOW_COLOR)
        self.__thirdPlayerTotal = sg.Text("", background_color=BRONZE_COLOR, text_color=YELLOW_COLOR)
        self.__fourthPlayerTotal = sg.Text("", background_color=RED_COLOR, text_color=YELLOW_COLOR)

        labelWidth = int(x/3)
        labelHeight = int(y/10)

        firstPlayer = sg.Frame("", [[sg.VPush(background_color=GOLD_COLOR)],
                                 [sg.Column([[self.__firstPlayerName, self.__firstPlayerGood, self.__firstPlayerBad, self.__firstPlayerTotal]])],
                                 [sg.VPush(background_color=GOLD_COLOR)]],
                                 background_color=GOLD_COLOR, size=(labelWidth-20, labelHeight), pad=10, element_justification="center")
        
        secondPlayer = sg.Frame("", [[sg.VPush(background_color=SILVER_COLOR)],
                                  [sg.Column([[self.__secondPlayerName, self.__secondPlayerGood, self.__secondPlayerBad, self.__secondPlayerTotal]])],
                                  [sg.VPush(background_color=SILVER_COLOR)]],
                                 background_color=SILVER_COLOR, size=(labelWidth-20, labelHeight), pad=10, element_justification="center")
        
        thirdPlayer = sg.Frame("", [[sg.VPush(background_color=BRONZE_COLOR)],
                                 [sg.Column([[self.__thirdPlayerName, self.__thirdPlayerGood, self.__thirdPlayerBad, self.__thirdPlayerTotal]])],
                                 [sg.VPush(background_color=BRONZE_COLOR)]],
                                background_color=BRONZE_COLOR, size=(labelWidth-20, labelHeight), pad=10, element_justification="center")
        
        fourthPlayer = sg.Frame("", [[sg.VPush(background_color=RED_COLOR)],
                                  [sg.Column([[self.__fourthPlayerName, self.__fourthPlayerGood, self.__fourthPlayerBad, self.__fourthPlayerTotal]])],
                                  [sg.VPush(background_color=RED_COLOR)]],
                                 background_color=RED_COLOR, size=(labelWidth-20, labelHeight), pad=10, element_justification="center")

        scoreLayout = [[firstPlayer], 
                       [secondPlayer],
                       [thirdPlayer],
                       [fourthPlayer]]
        
        scoreFrame = sg.Frame("", scoreLayout, border_width=0, background_color=LIGHT_GREY_COLOR, size=(labelWidth, 4 * (labelHeight + 20)), element_justification="center")

        scoreDisplayLayout = [[sg.VPush(background_color=BLACK_COLOR)],
                              [scoreFrame],
                              [sg.VPush(background_color=BLACK_COLOR)]]

        self.__scoreDisplayFrame = sg.Frame("", scoreDisplayLayout, border_width=0, background_color=BLACK_COLOR, pad=0, element_justification="center", visible=False, size=(x, y))

        self.__PSGLayout[0].append(self.__scoreDisplayFrame)

        ########################

        self.__PSGWindow = sg.Window('Display', self.__PSGLayout, element_justification='left', finalize=True, background_color=BLACK_COLOR, element_padding=0, return_keyboard_events=True, no_titlebar=True)
        self.__PSGWindow.Maximize()
        self.__PSGWindow.get_screen_size()

    def Update(self):
        event, values = self.__PSGWindow.read(0)
        if event != sg.TIMEOUT_KEY:
            if (event == sg.WIN_CLOSED):
                quit()
        elif event == 'Escape:27':
            quit()

    def SetQuestion(self, question, ansA, ansB, ansC, ansD):
        x, y = sg.Window.get_screen_size()

        questionLength = sg.Text.string_width_in_pixels("_ 3000", question)
        width = x - 80
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
        
        width = x/2 - 80
        fontSize = int(3000 * (width / lengthiest))
        fontStr = "_ "+str(fontSize)

        self.__ansAText.update(value=ansA, font=fontStr)
        self.__ansBText.update(value=ansB, font=fontStr)
        self.__ansCText.update(value=ansC, font=fontStr)
        self.__ansDText.update(value=ansD, font=fontStr)

        return

    def SetScore(self, fiName, fiGood, fiBad, sName, sGood, sBad, tName, tGood, tBad, foName, foGood, foBad):
        self.__firstPlayerName.update(fiName)
        self.__secondPlayerName.update(sName)
        self.__thirdPlayerName.update(tName)
        self.__fourthPlayerName.update(foName)

        self.__firstPlayerGood.update(str(fiGood))
        self.__secondPlayerGood.update(str(sGood))
        self.__thirdPlayerGood.update(str(tGood))
        self.__fourthPlayerGood.update(str(foGood))

        self.__firstPlayerBad.update(str(fiBad))
        self.__secondPlayerBad.update(str(sBad))
        self.__thirdPlayerBad.update(str(tBad))
        self.__fourthPlayerBad.update(str(foBad))

        self.__firstPlayerTotal.update(str(fiGood - fiBad))
        self.__secondPlayerTotal.update(str(sGood - sBad))
        self.__thirdPlayerTotal.update(str(tGood - tBad))
        self.__fourthPlayerTotal.update(str(foGood - foBad))

        self.__scoreDisplayFrame.update(visible=True)

test = QuestionDisplay()

#test.SetQuestion("Quelle est la taille du continum espace temps dans la série blargblargblarg ?", "La réponse A", "La grosse réponse B", "repC", "Et non pas la D")
test.SetScore("Bernard", 5, 3, "Jean-Dominique", 2, 7, "Bapt", 4, 4, "SheitMan", 8, 0)

while True:
    test.Update()
