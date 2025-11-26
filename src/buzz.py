from Settingator import *
from PySerialCommunicator import *
from TKDisplay import *
from PySimpleGUIDisplay import * 
import pygame.mixer as mx


BUZZ_BUTTON = 5

STAR_WARS = 1
DISNEY  = 2
LEGO = 3
MARVEL = 4
HARRY_POTTER = 5
X_MEN = 6
DBZ = 7
MARIO = 8


buzzed = True
buzzedTeam = 0
buzzedSlave = None

class Sound:
    def __init__(self):
        mx.init(channels=1)
        self.__channel = mx.Channel(0)
        self.__buzzSound = {
            STAR_WARS: mx.Sound("buzzSound/stw.wav"),
            DISNEY: mx.Sound("buzzSound/dny.wav"),
            LEGO: mx.Sound("buzzSound/lgo.wav"),
            MARVEL: mx.Sound("buzzSound/mcu.wav"),
            HARRY_POTTER: mx.Sound("buzzSound/hp.wav"),
            X_MEN: mx.Sound("buzzSound/xmn.wav"),
            DBZ: mx.Sound("buzzSound/dbz.wav"),
            MARIO: mx.Sound("buzzSound/mario.wav")
        }

        self.__validateSound = {
            STAR_WARS: mx.Sound("validate/Star wars bon.wav"),
            DISNEY: mx.Sound("validate/Disney bon.wav"),
            LEGO: mx.Sound("validate/Lego bon.wav"),
            MARVEL: mx.Sound("validate/Marvel bon.wav"),
            HARRY_POTTER: mx.Sound("validate/HP bon.wav"),
            X_MEN: mx.Sound("validate/Xmen bon.wav"),
            DBZ: mx.Sound("validate/Dbzbon.wav"),
            MARIO: mx.Sound("validate/Mario bon.wav")
        }

        self.__falseSound = {
            STAR_WARS: mx.Sound("validate/Star wars faux.wav"),
            DISNEY: mx.Sound("validate/Disney faux.wav"),
            LEGO: mx.Sound("validate/Lego faux.wav"),
            MARVEL: mx.Sound("validate/Marvel faux.wav"),
            HARRY_POTTER: mx.Sound("validate/HP faux.wav"),
            X_MEN: mx.Sound("validate/Xmen faux.wav"),
            DBZ: mx.Sound("validate/Dbz faux.wav"),
            MARIO: mx.Sound("validate/Mario faux.wav")
        }

        self.__citation = {
            STAR_WARS: mx.Sound("citation/cit_starwars.wav"),
            DISNEY: mx.Sound("citation/cit_disney.wav"),
            LEGO: mx.Sound("citation/cit_lego.wav"),
            MARVEL: mx.Sound("citation/cit_mcu.wav"),
            HARRY_POTTER: mx.Sound("citation/cit_hp.wav"),
            X_MEN: mx.Sound("citation/cit_xmen.wav"),
            DBZ: mx.Sound("citation/cit_dbz.wav"),
            MARIO: mx.Sound("citation/cit_mario.wav")
        }

        self.__bip = mx.Sound("sound/endWait.wav")

    def playBuzz(self, team:int):
        if team:
            self.__channel.play(self.__buzzSound[team])

    def validate(self, team:int):
        self.__channel.play(self.__validateSound[team])

    def falseAnswer(self, team:int):
        self.__channel.play(self.__falseSound[team])

    def playCit(self, team):
        self.__channel.play(self.__citation[team])

    def playBip(self):
        self.__channel.play(self.__bip)

soundModule = Sound()

def playHP(value):
    soundModule.playCit(HARRY_POTTER)

def playStarWars(value):
    soundModule.playCit(STAR_WARS)

def playDisney(value):
    soundModule.playCit(DISNEY)

def playLego(value):
    soundModule.playCit(LEGO)

def playMarvel(value):
    soundModule.playCit(MARVEL)

def playXMen(value):
    soundModule.playCit(X_MEN)

def playDBZ(value):
    soundModule.playCit(DBZ)

def playMario(value):
    soundModule.playCit(MARIO)

btPlayHP = LayoutElement(IDP_BUTTON, None, "playHP", callback=playHP)
btPlayStarWars = LayoutElement(IDP_BUTTON, None, "playStarWars", callback=playStarWars)
btPlayDisney = LayoutElement(IDP_BUTTON, None, "playDisney", callback=playDisney)
btPlayLego = LayoutElement(IDP_BUTTON, None, "playLego", callback=playLego)
btPlayMarvel = LayoutElement(IDP_BUTTON, None, "playMarvel", callback=playMarvel)
btPlayXMen = LayoutElement(IDP_BUTTON, None, "playXMen", callback=playXMen)
btPlayDBZ = LayoutElement(IDP_BUTTON, None, "playDBZ", callback=playDBZ)
btPlayMario = LayoutElement(IDP_BUTTON, None, "playMario", callback=playMario)

def ReInit(value):
    STR.BridgeReInitSlaves()

btReInit = LayoutElement(IDP_BUTTON, None, "reinitSlave", callback=ReInit)

def askQuestion(value):
    global buzzed
    buzzed = False
    if buzzedTeam:
        buzzedSlave.SendSettingUpdateByName("GREEN", 0)
        buzzedSlave.SendSettingUpdateByName("RED", 0)
        buzzedSlave.SendSettingUpdateByName("BLUE", 255)
        buzzedSlave.SendSettingUpdateByName("UPDATE_LED")
    soundModule.playBip()


def validate(value):
    if buzzedTeam:
        soundModule.validate(buzzedTeam)
        buzzedSlave.SendSettingUpdateByName("RED", 0)
        buzzedSlave.SendSettingUpdateByName("GREEN", 255)
        buzzedSlave.SendSettingUpdateByName("BLUE", 0)
        buzzedSlave.SendSettingUpdateByName("UPDATE_LED")


def invalidate(value):
    if buzzedTeam:
        soundModule.falseAnswer(buzzedTeam)
        buzzedSlave.SendSettingUpdateByName("RED", 255)
        buzzedSlave.SendSettingUpdateByName("GREEN", 0)
        buzzedSlave.SendSettingUpdateByName("BLUE", 0)
        buzzedSlave.SendSettingUpdateByName("UPDATE_LED")


validateBtn = LayoutElement(IDP_BUTTON, None, "validate", callback=validate)
invalidateBtn = LayoutElement(IDP_BUTTON, None, "invalidate", callback=invalidate)

askQuestionBtn = LayoutElement(IDP_BUTTON, None, "newQuestionBip", callback=askQuestion)

def buzzButton(slaveID:int):
    global buzzed 
    if (not buzzed):
        buzzed = True
        global buzzedSlave
        buzzedSlave = STR.GetSlave(slaveID)
        buzzedSlave.SendSettingUpdateByName("RED", 255)
        buzzedSlave.SendSettingUpdateByName("GREEN", 255)
        buzzedSlave.SendSettingUpdateByName("BLUE", 255)
        buzzedSlave.SendSettingUpdateByName("UPDATE_LED")
        
        print(buzzedSlave.GetSettingByName("TEAM").GetValue())
        global buzzedTeam
        buzzedTeam = buzzedSlave.GetSettingByName("TEAM").GetValue()

        soundModule.playBuzz(buzzedSlave.GetSettingByName("TEAM").GetValue())

def reloadAll(value):
    slaves = STR.GetSlaves()

    for id in slaves:
        slaves[id].SendInitRequest(id)

reloadButton = LayoutElement(IDP_BUTTON, None, "reload", callback=reloadAll)

def initBuzzer(slave):
    team = slave.GetSettingByName("TEAM").GetValue()

    if team:
        soundModule.playBuzz(team)

def sendInitRequestFunc(value):
    STR.SendInitRequest()

sendInitRequestButton = LayoutElement(IDP_BUTTON, None, "SendInitRequest", callback=sendInitRequestFunc)

def startBridgeInitFunc(value):
    STR.BridgeStartInitBroadcasted(initBuzzer)

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

if __name__ == "__main__":

    com = SerialCTR(PySimpleGUIDisplay.SelectCOMPort(SerialCTR))

    display = TKDisplay()

    STR = Settingator(com, display)



    STR.AddNotifCallback(BUZZ_BUTTON, buzzButton)

    STR.AddToLayout(askQuestionBtn)
    STR.AddToLayout(validateBtn)
    STR.AddToLayout(invalidateBtn)

    STR.AddToLayout(btPlayMarvel)
    STR.AddToLayout(btPlayDBZ)
    STR.AddToLayout(btPlayHP)
    STR.AddToLayout(btPlayDisney)
    STR.AddToLayout(btPlayLego)
    STR.AddToLayout(btPlayMario)
    STR.AddToLayout(btPlayXMen)
    STR.AddToLayout(btPlayStarWars)

    STR.AddToLayout(reloadButton)

    STR.AddToLayout(startBridgeInitButton)
    STR.AddToLayout(stopBridgeInitButton)

    STR.AddToLayout(sendInitRequestButton)

    STR.AddToLayout(btReInit)

    STR.AddToLayout(layoutDisplayCheck)

    #STR.SendInitRequest()

    while display.IsRunning():
        STR.Update()