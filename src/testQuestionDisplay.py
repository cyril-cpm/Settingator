import PySimpleGUI as sg

class QuestionDisplay():
    def __init__(self):

        self.__PSGLayout = [[],[]]

        x, y =sg.Window.get_screen_size()

        questionFrameLayout = [[sg.Text("Coucou")]]
        questionFrame = sg.Frame("", questionFrameLayout, border_width=0, background_color='#222222', expand_y=True, pad=10, size=(x- 20, 1))
        test = sg.Text.string_width_in_pixels("_ 12", "WESHHHHHHHHHHHHHHHHHHHH\nAlors")
        width = x/2 - 20
        fontSize = int(12 * (width / test))
        fontStr = "_ "+str(fontSize)

        ansAText = sg.Text("WESHHHHHHHHHH\nHHHHHHHHHH\nAlors", font=fontStr, background_color="#FF0000", expand_x=True, justification="center")
        ansAFrame = sg.Frame("", [[sg.VPush(background_color="#FF0000")],[ansAText], [sg.VPush(background_color="#FF0000")]], border_width=0, background_color='#FF0000', size=(int(x/2) - 20,1), expand_y=True, pad=10)
        ansBFrame = sg.Frame("", [[sg.Text("alors", background_color="#00FF00")]], border_width=0, background_color='#00FF00', size=(int(x/2) - 20,1), expand_y=True, pad=10)
        ansCFrame = sg.Frame("", [[]], border_width=0, background_color='#FFFF00', size=(int(x/2) - 20,1), expand_y=True, pad=10)
        ansDFrame = sg.Frame("", [[]], border_width=0, background_color='#0000FF', size=(int(x/2) - 20,1), expand_y=True, pad=10)

        answerFrameLayout = [[],[]]
        answerFrameLayout[0].append(ansAFrame)
        answerFrameLayout[0].append(ansBFrame)
        answerFrameLayout[1].append(ansCFrame)
        answerFrameLayout[1].append(ansDFrame)

        answerFrame = sg.Frame("", answerFrameLayout, border_width=0, background_color='#666666', size=(x - 20,1), expand_y=True, pad=10)

        self.__PSGLayout[0].append(questionFrame)
        self.__PSGLayout[1].append(answerFrame)

        self.__PSGWindow = sg.Window('Display', self.__PSGLayout, element_justification='left', finalize=True, background_color='#000000')
        self.__PSGWindow.Maximize()
        self.__PSGWindow.get_screen_size()

    def Update(self):
        event, values = self.__PSGWindow.read(0)
        if event != sg.TIMEOUT_KEY:
            if (event == sg.WIN_CLOSED):
                quit()

test = QuestionDisplay()

while True:
    test.Update()
