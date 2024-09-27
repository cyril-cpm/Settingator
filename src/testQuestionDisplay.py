import PySimpleGUI as sg

class QuestionDisplay():
    def __init__(self):

        self.__PSGLayout = [[],[]]


        questionFrameLayout = [[sg.Text("Coucou")]]
        questionFrame = sg.Frame("", questionFrameLayout, border_width=0, background_color='#222222', expand_x=True, expand_y=True)

        ansAFrame = sg.Frame("", [[sg.Text("Réponse A", vertical_alignment="center")]], border_width=0, background_color='#FF0000', expand_x=True, expand_y=True, element_justification="center")
        ansBFrame = sg.Frame("", [[]], border_width=0, background_color='#00FF00', expand_x=True, expand_y=True)
        ansCFrame = sg.Frame("", [[]], border_width=0, background_color='#FFFF00', expand_x=True, expand_y=True)
        ansDFrame = sg.Frame("", [[]], border_width=0, background_color='#0000FF', expand_x=True, expand_y=True)

        answerFrameLayout = [[],[]]
        answerFrameLayout[0].append(ansAFrame)
        answerFrameLayout[0].append(ansBFrame)
        answerFrameLayout[1].append(ansCFrame)
        answerFrameLayout[1].append(ansDFrame)

        answerFrame = sg.Frame("", answerFrameLayout, border_width=0, background_color='#666666', expand_x=True, expand_y=True)

        self.__PSGLayout[0].append(questionFrame)
        self.__PSGLayout[1].append(answerFrame)

        self.__PSGWindow = sg.Window('Display', self.__PSGLayout, element_justification='left', finalize=True, background_color='#000000')
        self.__PSGWindow.Maximize()

    def Update(self):
        event, values = self.__PSGWindow.read(0)
        if event != sg.TIMEOUT_KEY:
            if (event == sg.WIN_CLOSED):
                quit()

test = QuestionDisplay()

while True:
    test.Update()
