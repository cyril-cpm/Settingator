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

buzzed = False
resetted = False
buzzerActivated = False

buzzedSlave = None
blockedSlave:dict = {}

gunForInvalidation = False
gunForTooEarlyBuzz = False
gunForValidation = False
songQuizz = False

separateResetAndActivate = True
punishBuzzBeforeDing = False

def punishBuzzBeforeDingFunc(value):
	global punishBuzzBeforeDing
	punishBuzzBeforeDing = bool(int(value))

punishBuzzBeforeDingCheck = LayoutElement(
		IDP_CHECK,
		None,
		"Punish Buzzer for too early buzz",
		callback=punishBuzzBeforeDingFunc
	)

def separateResetAndActivateFunc(value):
	global separateResetAndActivate
	separateResetAndActivate = bool(int(value))

separateResetAndActivateCheck = LayoutElement(
		IDP_CHECK,
		separateResetAndActivate,
		"Separate reset and activate",
		callback=separateResetAndActivateFunc
	)

def songQuizzFunc(value):
	global songQuizz
	songQuizz = bool(int(value))

songQuizzCheck = LayoutElement(
		IDP_CHECK,
		None,
		"Song Quizz",
		callback=songQuizzFunc
	)

def gunForValidationFunc(value):
	global gunForValidation
	gunForValidation = bool(int(value))

gunForValidationCheck = LayoutElement(
		IDP_CHECK,
		None,
		"Gun when good",
		callback=gunForValidationFunc
		)

def gunForTooEarlyBuzzFunc(value):
	global gunForTooEarlyBuzz
	gunForTooEarlyBuzz = bool(int(value))

gunForTooEarlyBuzzCheck = LayoutElement(
		IDP_CHECK,
		None,
		"Gun when too early buzz",
		callback=gunForTooEarlyBuzzFunc
	)

def gunForInvalidationFunc(value):
	global gunForInvalidation
	gunForInvalidation = bool(int(value))

gunForInvalidationCheck = LayoutElement(
		IDP_CHECK,
		None,
		"Gun when false",
		callback = gunForInvalidationFunc
	)

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

layoutDisplayCheck = LayoutElement(IDP_CHECK, True, "DisplayLayout", callback=displayLayout)

def initModule(slave:Slave):
	rgbSetting = slave.GetSettingByName("__RGB")

	if rgbSetting != None:
		if slave.GetID() not in blockedSlave:
			blockedSlave[slave.GetID()] = 0.0

		slave.SendSettingUpdateByName("__RGB", rgbSetting.GetValue())

def buzzButton(slaveID:int):
	global buzzed
	global resetted
	global buzzedSlave
	global chan
	global buzzerActivated
	global punishBuzzBeforeDing

	if slaveID not in blockedSlave:
		blockedSlave[slaveID] = 0.0

	if time.time() - blockedSlave[slaveID] > 2.5:

		if punishBuzzBeforeDing and not buzzed and not buzzerActivated:
			global buzzedSlave
			buzzedSlave = STR.GetSlave(slaveID)
			if buzzedSlave:

				if gunForTooEarlyBuzz:
					gunSlave = STR.GetSlaveWithSetting("SHOOT_A")

					if gunSlave != None:
						if buzzedSlave.GetID() == shootAID:
							gunSlave.SendSettingUpdateByName("SHOOT_A", None)

						elif buzzedSlave.GetID() == shootBID:
							gunSlave.SendSettingUpdateByName("SHOOT_B", None)
							
				blockedSlave[slaveID] = time.time()
				buzzedSlave.SendSettingUpdateByName("__RGB", 0xFF0000)

				global invalidateSound
				chan.play(invalidateSound)
			
		elif not buzzed and buzzerActivated:
			buzzerActivated = False
			buzzed = True
			resetted = False
			buzzedSlave = STR.GetSlave(slaveID)
			if buzzedSlave:
				buzzedSlave.SendSettingUpdateByName("__RGB", 0XFFFFFF)
				global buzzSound
				chan.play(buzzSound)

def resetBuzzerFunc(value):
	global resetted
	resetted = True
	global buzzed
	buzzed = False
	global buzzedSlave
	buzzedSlave = None
	global separateResetAndActivate
	global buzzerActivated

	if not separateResetAndActivate:
		buzzerActivated = True

	global playedSong

	if not songIndex in playedSong:
		playedSong.append(songIndex)

		if songNameLabel.GetIElement():
			songNameLabel.GetIElement().SetBGColor("lightgreen")

	slaves = STR.GetSlaves()

	if slaves:
		for slaveID in slaves:
			slave = STR.GetSlave(slaveID)

			if slave and slave.GetSettingByName("__RGB") != None:
				slave.SendSettingUpdateByName("__RGB", 0x0000FF)
				# time.sleep(0.1)

def activateBuzzerFunc(value):
	global buzzed
	buzzed = False
	global resetted
	resetted = False
	global buzzerActivated
	buzzerActivated = True

	global separateResetAndActivate
	if not separateResetAndActivate:
		resetBuzzerFunc(None)

	global chan
	global activateSound
	chan.play(activateSound)

def validateQuestionFunc(value):
	global buzzedSlave
	if buzzedSlave:
		buzzedSlave.SendSettingUpdateByName("__RGB", 0x00FF00)

		global chan
		global validateSound
		global songSound

		if gunForValidation:
			gunSlave = STR.GetSlaveWithSetting("SHOOT_A")

			if gunSlave != None:
				if shootAID != 0 and buzzedSlave.GetID() != shootAID:
					gunSlave.SendSettingUpdateByName("SHOOT_A", None)

				if shootBID != 0 and buzzedSlave.GetID() != shootBID:
					gunSlave.SendSettingUpdateByName("SHOOT_B", None)


		if songQuizz:
			chan.play(songSound)
		else:
			chan.play(validateSound)

def invalidateQuestionFunc(value):
	global buzzedSlave
	if buzzedSlave:
		buzzedSlave.SendSettingUpdateByName("__RGB", 0xFF0000)
		global chan
		global invalidateSound
		chan.play(invalidateSound)
		global resetted
		global buzzed
		resetted = False
		buzzed = False
		global buzzerActivated
		buzzerActivated = True
		global blockedSlave
		blockedSlave[buzzedSlave.GetID()] = time.time()

		if gunForInvalidation:
			gunSlave = STR.GetSlaveWithSetting("SHOOT_A")

			if gunSlave != None:
				if buzzedSlave.GetID() == shootAID:
					gunSlave.SendSettingUpdateByName("SHOOT_A", None)

				elif buzzedSlave.GetID() == shootBID:
					gunSlave.SendSettingUpdateByName("SHOOT_B", None)

resetBuzzer = LayoutElement(IDP_BUTTON, None, "Reset Buzzer", callback=resetBuzzerFunc)
activateBuzzer = LayoutElement(IDP_BUTTON, None, "Activate Buzzer", callback=activateBuzzerFunc)
validateQuestion = LayoutElement(IDP_BUTTON, None, "Validate", callback=validateQuestionFunc)
invalidateQuestion = LayoutElement(IDP_BUTTON, None, "Invalidate", callback=invalidateQuestionFunc)



def checkBlockedSlave() -> None:
	global blockedSlave

	for slaveID in blockedSlave:
		if blockedSlave[slaveID] != 0.0 and time.time() - blockedSlave[slaveID] > 2.5:
			blockedSlave[slaveID] = 0.0
			slave: Slave | None = STR.GetSlave(slaveID)
			if slave:
				slave.SendSettingUpdateByName("__RGB", 0x0000FF)

songColumn = LayoutElement(IDP_COLUMN, None, "Sélection de Chanson")

def setSong(index):
	global songIndex
	global songName
	global validateSound
	global songNameLabel
	global songSound

	if (index >= 0):
		songIndex = index

		name = getFile(songIndex, "../musik")

		if name:
			songName = name
			songNameLabel.UpdateValue(songName)
			songSound = mx.Sound("../musik/" + songName)
		else:
			songName = str(songIndex) + " Non trouvée"
			songNameLabel.UpdateValue(songName)
			songSound = mx.Sound("../good.wav")

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

shootAID = 0
shootBID = 0

def updateShootAID(value):
	global shootAID
	shootAID = int(value)

def updateShootBID(value):
	global shootBID
	shootBID = int(value)

shootASlaveID = LayoutElement(
		IDP_FRAME,
		None,
		children=[
			LayoutElement(IDP_TEXT, "ShootA ID"),
			LayoutElement(IDP_INPUT, None, callback=updateShootAID)
		]
	)

shootBSlaveID = LayoutElement(
		IDP_FRAME,
		None,
		children=[
			LayoutElement(IDP_TEXT, "ShootB ID"),
			LayoutElement(IDP_INPUT, None, callback=updateShootBID)
		]
	)

gunColumn = LayoutElement(
		IDP_COLUMN,
		None,
		"Gun Config",
		children=[
			shootASlaveID,
			shootBSlaveID
		]
	)

if __name__ == "__main__":

	# com = ICTR()
	com = SerialCTR("/dev/ttyUSB0")

	mx.init(channels=1)
	global chan
	chan = mx.Channel(0)

	global validateSound
	validateSound = mx.Sound("../good.wav")

	global songSound
	songSound = mx.Sound("../good.wav")

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

	STR.AddToLayout(songColumn)

	STR.AddToLayout(
			LayoutElement(
				IDP_COLUMN,
				None,
				"Rules",
				children=[
					punishBuzzBeforeDingCheck,
					separateResetAndActivateCheck,
					songQuizzCheck,
					gunForValidationCheck,
					gunForInvalidationCheck,
					gunForTooEarlyBuzzCheck
				]
			)
		)

	STR.AddToLayout(gunColumn)

	STR.AddToLayout(startBridgeInitButton)
	STR.AddToLayout(stopBridgeInitButton)

	STR.AddToLayout(layoutDisplayCheck)

	setSong(0)


	while display.IsRunning():
		STR.Update()
		checkBlockedSlave()
