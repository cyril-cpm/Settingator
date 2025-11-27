from Settingator import *
from PySerialCommunicator import *
from TKDisplay import *
import time
import random
from pygame import mixer as mx



BUZZ_BUTTON = 5

buzzed = True
buzzedSlave = None

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


def initModule(slave:Slave):
	if slave.GetSettingByName("TEAM") != None:
		slave.SendSettingUpdatesByName([("RED", 0),
										("GREEN", 0),
										("BLUE", 255),
										("UPDATE_LED", None)])

def buzzButton(slaveID:int):
	global buzzed
	if not buzzed:
		global buzzedSlave
		buzzed = True
		buzzedSlave = STR.GetSlave(slaveID)
		if buzzedSlave:
			buzzedSlave.SendSettingUpdatesByName([("RED", 255),
												("GREEN", 255),
												("BLUE", 255),
												("UPDATE_LED", None)])
			global buzzSound
			global chan
			chan.play(buzzSound)

def resetBuzzerFunc(value):
	global buzzedSlave
	if buzzedSlave:
			buzzedSlave.SendSettingUpdatesByName([("RED", 0),
												("GREEN", 0),
												("BLUE", 255),
												("UPDATE_LED", None)])

def activateBuzzerFunc(value):
	global buzzed
	buzzed = False

	global chan
	global activateSound
	chan.play(activateSound)

def validateQuestionFunc(value):
	global buzzedSlave
	if buzzedSlave:
		buzzedSlave.SendSettingUpdatesByName([("RED", 0),
											("GREEN", 255),
											("BLUE", 0),
											("UPDATE_LED", None)])
		global chan
		global validateSound
		chan.play(validateSound)

def invalidateQuestionFunc(value):
	global buzzedSlave
	if buzzedSlave:
		buzzedSlave.SendSettingUpdatesByName([("RED", 255),
											("GREEN", 0),
											("BLUE", 0),
											("UPDATE_LED", None)])
		global chan
		global invalidateSound
		chan.play(invalidateSound)

resetBuzzer = LayoutElement(IDP_BUTTON, None, "Reset Buzzer", callback=resetBuzzerFunc)
activateBuzzer = LayoutElement(IDP_BUTTON, None, "Activate Buzzer", callback=activateBuzzerFunc)
validateQuestion = LayoutElement(IDP_BUTTON, None, "Validate", callback=validateQuestionFunc)
invalidateQuestion = LayoutElement(IDP_BUTTON, None, "Invalidate", callback=invalidateQuestionFunc)


if __name__ == "__main__":

	com = SerialCTR("/dev/ttyUSB0")

	mx.init(channels=1)
	global chan
	chan = mx.Channel(0)

	global validateSound
	validateSound = mx.Sound("../good.wav")

	global invalidateSound
	invalidateSound = mx.Sound("../bad.wav")

	global activateSound
	activateSound = mx.Sound("../endWait.wav")

	global buzzSound
	buzzSound = mx.Sound("../stw.wav")

	display = TKDisplay()

	STR = Settingator(com, display)


	STR.AddNotifCallback(BUZZ_BUTTON, buzzButton)

	STR.AddToLayout(LayoutElement(IDP_COLUMN, None, "Control", children=[
		resetBuzzer,
		activateBuzzer,
		validateQuestion,
		invalidateQuestion
		]))

	STR.AddToLayout(reloadButton)

	STR.AddToLayout(startBridgeInitButton)
	STR.AddToLayout(stopBridgeInitButton)

	STR.AddToLayout(sendInitRequestButton)

	STR.AddToLayout(btReInit)

	STR.AddToLayout(layoutDisplayCheck)

	while display.IsRunning():
		STR.Update()
