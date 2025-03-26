from Settingator import *
from PySerialCommunicator import *
from PySimpleGUIDisplay import *

com:SerialCTR

display:PySimpleGUIDisplay

STR:Settingator

if __name__ == "__main__":
    com = SerialCTR(PySimpleGUIDisplay.SelectCOMPort(SerialCTR))

    display = PySimpleGUIDisplay()
    
    STR = Settingator(com, display)

    display.UpdateLayout(None)

    STR.SendInitRequest(1)

    while display.isRunning():
        STR.Update()