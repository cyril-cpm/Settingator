import STRLog
from STRLog import STRMessgeLog
from Settingator import *
from PySerialCommunicator import *
from TKDisplay import *
import time
import random
from pygame import mixer as mx
from Log import Logger

from pathlib import Path

def getFile(index, dossier_cible="."):
    """
    Recherche un fichier commençant par 'index ' dans le dossier spécifié.
    """
    # On crée un objet Path pour le dossier
    chemin_dossier = Path(dossier_cible)
    
    # On itère sur tous les fichiers du dossier
    for fichier in chemin_dossier.iterdir():
        # On vérifie si c'est un fichier (pas un dossier)
        if fichier.is_file():
            # On sépare le nom pour vérifier le début
            # Exemple: "1 fichier 1.txt" -> "1"
            prefixe = fichier.name.split(' ')[0]
            
            if prefixe == str(index):
                return fichier.name
                
    return None

# Exemple d'utilisation :
# nom = recuperer_nom_fichier(2)
# print(nom) # Affiche "2 le second fichier.ext"

songIndex = 1
songName = "Non trouvée"
playedSong = []

BUZZ_BUTTON = 5

buzzed = True
buzzedSlave = None
resetted = False
blockedSlave:dict = {}

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
		if slave.GetID() not in blockedSlave:
			blockedSlave[slave.GetID()] = 0.0

		slave.SendSettingUpdatesByName([("RED", 0),
										("GREEN", 0),
										("BLUE", 255),
										("UPDATE_LED", None)])

def buzzButton(slaveID:int):
	global buzzed
	global resetted
	global buzzedSlave
	global chan

	if slaveID not in blockedSlave:
		blockedSlave[slaveID] = 0.0

	if time.time() - blockedSlave[slaveID] > 2.5:

		if buzzed and resetted:
			global buzzedSlave
			buzzedSlave = STR.GetSlave(slaveID)
			if buzzedSlave:
				blockedSlave[slaveID] = time.time()
				buzzedSlave.SendSettingUpdatesByName([("RED", 255),
													("GREEN",0),
													("BLUE", 0),
													("UPDATE_LED", None)])
				global invalidateSound
				chan.play(invalidateSound)
			
		if not buzzed:
			buzzed = True
			resetted = False
			buzzedSlave = STR.GetSlave(slaveID)
			if buzzedSlave:
				buzzedSlave.SendSettingUpdatesByName([("RED", 255),
													("GREEN", 255),
													("BLUE", 255),
													("UPDATE_LED", None)])
				global buzzSound
				chan.play(buzzSound)

def resetBuzzerFunc(value):
	global resetted
	resetted = True
	global buzzed
	buzzed = False

	global playedSong

	if not songIndex in playedSong:
		playedSong.append(songIndex)

		if songNameLabel.GetIElement():
			songNameLabel.GetIElement().SetBGColor("lightgreen")

	slaves = STR.GetSlaves()

	if slaves:
		for slaveID in slaves:
			slave = STR.GetSlave(slaveID)

			if slave:
				slave.SendSettingUpdatesByName([("RED", 0),
												("GREEN", 0),
												("BLUE", 255),
												("UPDATE_LED", None)])
				time.sleep(0.1)

def activateBuzzerFunc(value):
	global buzzed
	buzzed = False
	global resetted
	resetted = False

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
		global resetted
		global buzzed
		resetted = True
		buzzed = False
		global blockedSlave
		blockedSlave[buzzedSlave.GetID()] = time.time()

resetBuzzer = LayoutElement(IDP_BUTTON, None, "Reset Buzzer", callback=resetBuzzerFunc)
activateBuzzer = LayoutElement(IDP_BUTTON, None, "Activate Buzzer", callback=resetBuzzerFunc)
validateQuestion = LayoutElement(IDP_BUTTON, None, "Validate", callback=validateQuestionFunc)
invalidateQuestion = LayoutElement(IDP_BUTTON, None, "Invalidate", callback=invalidateQuestionFunc)

def logTestFunc(value):
	STR.SendInitRequest(None, 1)
	
def checkBlockedSlave() -> None:
	global blockedSlave

	for slaveID in blockedSlave:
		if blockedSlave[slaveID] != 0.0 and time.time() - blockedSlave[slaveID] > 2.5:
			blockedSlave[slaveID] = 0.0
			slave: Slave | None = STR.GetSlave(slaveID)
			if slave:
				slave.SendSettingUpdatesByName([("RED", 0),
												("GREEN", 0),
												("BLUE", 255),
												("UPDATE_LED", None)])

songColumn = LayoutElement(IDP_COLUMN, None, "Sélection de Chanson")

def setSong(index):
	global songIndex
	global songName
	global validateSound
	global songNameLabel

	if (index >= 0):
		songIndex = index

		name = getFile(songIndex, "../musik")

		if name:
			songName = name
			songNameLabel.UpdateValue(songName)
			validateSound = mx.Sound("../musik/" + songName)
		else:
			songName = str(songIndex) + " Non trouvée"
			songNameLabel.UpdateValue(songName)
			validateSound = mx.Sound("../good.wav")

		if songNameLabel.GetIElement():
			if songIndex in playedSong:
				songNameLabel.GetIElement().SetBGColor("lightgreen")

			else:
				songNameLabel.GetIElement().SetBGColor("lightgrey")

def prevSongFunc(value):
	global songIndex

	setSong(songIndex - 1)

prevSongButton = LayoutElement(IDP_BUTTON, None, "précédent", callback=prevSongFunc)

def nextSongFunc(value):
	global songIndex

	setSong(songIndex + 1)

nextSongButton = LayoutElement(IDP_BUTTON, None, "suivant", callback=nextSongFunc)

songNameLabel = LayoutElement(IDP_TEXT, songName, "fichier")

def selectSongIndex(value):
	setSong(int(value))

selectSongInput = LayoutElement(IDP_INPUT, None, callback=selectSongIndex)

songColumn.AppendElements([prevSongButton, selectSongInput, songNameLabel, nextSongButton])

if __name__ == "__main__":

	# com = ICTR()
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
		# activateBuzzer,
		validateQuestion,
		invalidateQuestion
		]))

	STR.AddToLayout(songColumn)

	STR.AddToLayout(startBridgeInitButton)
	STR.AddToLayout(stopBridgeInitButton)

	STR.AddToLayout(layoutDisplayCheck)

	setSong(0)


	while display.IsRunning():
		STR.Update()
		checkBlockedSlave()
