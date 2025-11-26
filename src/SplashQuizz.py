from Settingator import *
from PySerialCommunicator import *
from TKDisplay import *
import time
import random


BUZZ_BUTTON = 5

buzzed = True
buzzedTeam = 0
buzzedSlave = None

def delay():
    time.sleep(0.05)

def ReInit(value):
    STR.BridgeReInitSlaves()

btReInit = LayoutElement(IDP_BUTTON, None, "reinitSlave", callback=ReInit)

def reloadAll(value):
    slaves = STR.GetSlaves()

    for id in slaves:
        STR.SendInitRequest(None, id)

reloadButton = LayoutElement(IDP_BUTTON, None, "reload", callback=reloadAll)

def sendInitRequestFunc(value):
    STR.SendInitRequest()

sendInitRequestButton = LayoutElement(IDP_BUTTON, None, "SendInitRequest", callback=sendInitRequestFunc)

def startBridgeInitFunc(value):
    STR.BridgeStartInitBroadcasted(initModule)

def stopBridgeInitFunc(value):
    STR.BridgeStopInitBroadcasted()


startBridgeInitButton = LayoutElement(IDP_BUTTON, None, "StartBridgeInit", callback=startBridgeInitFunc)
stopBridgeInitButton = LayoutElement(IDP_BUTTON, None, "StopBridgeInit", callback=stopBridgeInitFunc)

def displayLayout(value):
    if int(value):
        STR.DisplaySlaveLayout()
    else:
        STR.RemoveSlaveLayout()

layoutDisplayCheck = LayoutElement(IDP_CHECK, None, "DisplayLayout", callback=displayLayout)


def initModule(slave):
    if slave.GetSettingByName("TEAM") != None:

        slave.SendSettingUpdateByName("RED", 0)
        delay()
        slave.SendSettingUpdateByName("GREEN", 0)
        delay()
        slave.SendSettingUpdateByName("BLUE", 0)
        delay()
        slave.SendSettingUpdateByName("UPDATE_LED")
        delay()

def buzzButton(slaveID:int):
    buzzSlave = STR.GetSlave(slaveID)
    
def introAButtonCB(value):
    module = STR.GetSlaveWithSetting("LEDMODULE")

    if module:
        module.SendSettingUpdatesByName([("INTRO_STACK", None),
                                         ("8INTRO_FORWARD_TRANSI_RATE_TRANSITION", None),
                                         ("9INTRO_BACKWARD_TRANSI_RATE_TRANSITION", None)])

introAButton = LayoutElement(IDP_BUTTON, None, "IntroA", callback=introAButtonCB)

if __name__ == "__main__":

    com = SerialCTR("/dev/ttyUSB0")

    display = TKDisplay()

    STR = Settingator(com, display)


    STR.AddNotifCallback(BUZZ_BUTTON, buzzButton)

    STR.AddToLayout(introAButton)

    STR.AddToLayout(reloadButton)

    STR.AddToLayout(startBridgeInitButton)
    STR.AddToLayout(stopBridgeInitButton)

    STR.AddToLayout(sendInitRequestButton)

    STR.AddToLayout(btReInit)

    STR.AddToLayout(layoutDisplayCheck)

    STR.BridgeStartInitBroadcasted(initModule)

    while display.IsRunning():
        STR.Update()
