from PySerialCommunicator import GetPortList, SerialCTR
from Settingator import *
from TKDisplay import *
from pygame import display, mixer as mx

BUZZ_BUTTON = 5

class GameRules:
	def __init__(self):
		self.gunForInvalidation = False
		self.gunForTooEarlyBuzz = False
		self.gunForValidation = False
		self.separateResetAndActivate = True
		self.punishBuzzBeforeDing = False

gameRules = GameRules()

class GameState:
	def __init__(self):
		self.buzzed = False
		self.resetted = False
		self.buzzedSlave:Slave|None = None
		self.buzzerActivated = False
		self.blockedSlave:dict = {}

gameState = GameState()

class GameSound:
	def __init__(self):
		self.validate = mx.Sound("../good.wav")
		self.invalidate = mx.Sound("../bad.wav")
		self.activate = mx.Sound("../endWait.wav")
		self.buzz = mx.Sound("../stw.wav")

def punishBuzzBeforeDingFunc(value):
	gameRules.punishBuzzBeforeDing = bool(int(value))

punishBuzzBeforeDingCheck = LayoutElement(
		IDP_CHECK,
		None,
		"Punish Buzzer for too early buzz",
		callback=punishBuzzBeforeDingFunc
	)

def separateResetAndActivateFunc(value):
	gameRules.separateResetAndActivate = bool(int(value))

separateResetAndActivateCheck = LayoutElement(
		IDP_CHECK,
		gameRules.separateResetAndActivate,
		"Separate reset and activate",
		callback=separateResetAndActivateFunc
	)

def gunForValidationFunc(value):
	gameRules.gunForValidation = bool(int(value))

gunForValidationCheck = LayoutElement(
		IDP_CHECK,
		None,
		"Gun when good",
		callback=gunForValidationFunc
		)

def gunForTooEarlyBuzzFunc(value):
	gameRules.gunForTooEarlyBuzz = bool(int(value))

gunForTooEarlyBuzzCheck = LayoutElement(
		IDP_CHECK,
		None,
		"Gun when too early buzz",
		callback=gunForTooEarlyBuzzFunc
	)

def gunForInvalidationFunc(value):
	gameRules.gunForInvalidation = bool(int(value))

gunForInvalidationCheck = LayoutElement(
		IDP_CHECK,
		None,
		"Gun when false",
		callback = gunForInvalidationFunc
	)

class PlayerConfig:
	def __init__(self):
		self.activated = True
		self.buzzerID = 0
		self.motorID = 0
		self.pwmID = 0

playerConfigs = {}

def activatePlayer(playerID:int, value:int):
	if playerID not in playerConfigs:
		playerConfigs[playerID] = PlayerConfig()

	playerConfigs[playerID].activated = int(value)

def setPlayerBuzID(playerID:int, value:int):
	if playerID not in playerConfigs:
		playerConfigs[playerID] = PlayerConfig()

	playerConfigs[playerID].buzzerID = value

def setPlayerMotID(playerID:int, value:int):
	if playerID not in playerConfigs:
		playerConfigs[playerID] = PlayerConfig()

	playerConfigs[playerID].motorID = value


def setPlayerPWMID(playerID:int, value:int):
	if playerID not in playerConfigs:
		playerConfigs[playerID] = PlayerConfig()

	playerConfigs[playerID].pwmID = value


def resetPlayerCount(value):
	Logger.Log("reseting player count", "PLAYER", "INFO")

	currentChildrenCount = 0
	children = playerLayout.GetChildren()

	if children:
		currentChildrenCount = children.__len__()

	if (int(value) > currentChildrenCount):
		for i in range(currentChildrenCount, int(value)):
			playerLayout.AppendElement(
					LayoutElement(
						IDP_COLUMN,
						None,
						"Player " + str(i+1),
						stick="w",
						children=[
							LayoutElement(
								IDP_CHECK,
								True,
								"Activated",
								callback=lambda v, id=i : activatePlayer(id, v)
								),
							LayoutElement(
								IDP_FRAME,
								None,
								"",
								stick='e',
								children=[
									LayoutElement(
										IDP_TEXT,
										"Buzzer SlaveID",
										""
										),
									LayoutElement(
										IDP_INPUT,
										0,
										"",
										callback=lambda v, id=i:setPlayerBuzID(id, int(v))
										)
									]
								),
							LayoutElement(
								IDP_FRAME,
								None,
								"",
								stick='e',
								children=[
									LayoutElement(
										IDP_TEXT,
										"Motor SlaveID",
										""
										),
									LayoutElement(
										IDP_INPUT,
										0,
										"",
										callback=lambda v, id=i:setPlayerMotID(id, int(v))
										),
									]
								),
							LayoutElement(
								IDP_FRAME,
								None,
								"",
								stick='e',
								children=[
									LayoutElement(
										IDP_TEXT,
										"PWM ID",
										""
										),
									LayoutElement(
										IDP_INPUT,
										-1,
										"",
										callback=lambda v, id=i:setPlayerPWMID(id, int(v))
										)
									]
								)
							]
						)
					)


	elif (int(value) < currentChildrenCount and children):
		for i in range(int(value), currentChildrenCount):
			del playerConfigs[i]
			playerLayout.RemoveElement(children[children.__len__()-1])

	else:
		Logger.Log("Nothing to do", "PLAYER", "INFO")

playerCount = LayoutElement(
		IDP_INPUT,
		2,
		"Player Count",
		callback = resetPlayerCount
	)

playerLayout = LayoutElement(IDP_FRAME, None, "")

def buzzButton(slaveID:int):

	if slaveID not in gameState.blockedSlave:
		gameState.blockedSlave[slaveID] = 0.0

	if time.time() - gameState.blockedSlave[slaveID] > 2.5:

		thePlayer = None

		for player in playerConfigs:
			if playerConfigs[player].buzzerID == slaveID:
				thePlayer = playerConfigs[player]
				break

		if thePlayer and thePlayer.activated \
			and gameRules.punishBuzzBeforeDing \
			and not gameState.buzzed \
			and not gameState.buzzerActivated:

			gameState.buzzedSlave = STR.GetSlave(slaveID)
			if gameState.buzzedSlave:

				if gameRules.gunForTooEarlyBuzz:
					gunSlave = STR.GetSlave(thePlayer.motorID)

					if gunSlave:
						pwmID = thePlayer.pwmID
						gunSlave.SendSettingUpdateByName("SHOOT", 1 << pwmID)

				gameState.blockedSlave[slaveID] = time.time()
				gameState.buzzedSlave.SendSettingUpdateByName("__RGB", 0xFF0000)

				if chan:
					chan.play(sound.invalidate)
			
		elif thePlayer and thePlayer.activated \
			and not gameState.buzzed and gameState.buzzerActivated:
			gameState.buzzerActivated = False
			gameState.buzzed = True
			gameState.resetted = False
			gameState.buzzedSlave = STR.GetSlave(slaveID)

			if gameState.buzzedSlave:
				gameState.buzzedSlave.SendSettingUpdateByName("__RGB", 0XFFFFFF)

				if chan:
					chan.play(sound.buzz)

def resetBuzzerFunc(value):
	gameState.resetted = True
	gameState.buzzed = False
	gameState.buzzedSlave = None

	if not gameRules.separateResetAndActivate:
		gameState.buzzerActivated = True

	slaves = STR.GetSlaves()

	if slaves:
		for slaveID in slaves:
			slave = STR.GetSlave(slaveID)

			if slave and slave.GetSettingByName("__RGB") != None:
				slave.SendSettingUpdateByName("__RGB", 0x0000FF)
				# time.sleep(0.1)

def activateBuzzerFunc(value):
	gameState.buzzed = False
	gameState.resetted = False
	gameState.buzzerActivated = True

	if not gameRules.separateResetAndActivate:
		resetBuzzerFunc(None)

	if chan:
		chan.play(sound.activate)

def validateQuestionFunc(value):
	if gameState.buzzedSlave:
		gameState.buzzedSlave.SendSettingUpdateByName("__RGB", 0x00FF00)

		buzzerSlaveID = gameState.buzzedSlave.GetID()

		if gameRules.gunForValidation:
			shootList = {}

			for key in playerConfigs:
				player = playerConfigs[key]

				if player.buzzerID != buzzerSlaveID and player.activated:
					if player.motorID not in shootList:
						shootList[player.motorID] = 0

					shootList[player.motorID] += 1 << player.pwmID

			for motorID in shootList:
				shootSlave = STR.GetSlave(motorID)

				if shootSlave:
					shootSlave.SendSettingUpdateByName("SHOOT", shootList[motorID])

		if chan:
			chan.play(sound.validate)

def invalidateQuestionFunc(value):
	if gameState.buzzedSlave:
		gameState.buzzedSlave.SendSettingUpdateByName("__RGB", 0xFF0000)
		gameState.resetted = False
		gameState.buzzed = False
		gameState.buzzerActivated = True
	
		slaveID = gameState.buzzedSlave.GetID()

		if chan:
			chan.play(sound.invalidate)

		gameState.blockedSlave[slaveID] = time.time()

		if gameRules.gunForInvalidation:
			for player in playerConfigs:
				if playerConfigs[player].buzzerID == slaveID:
					if playerConfigs[player].activated:
						gunSlave = STR.GetSlave(playerConfigs[player].motorID)

						if (gunSlave):
							pwmID = playerConfigs[player].pwmID
							gunSlave.SendSettingUpdateByName("SHOOT", 1 << pwmID)

					break;

def checkBlockedSlave() -> None:

	for slaveID in gameState.blockedSlave:
		if gameState.blockedSlave[slaveID] != 0.0 \
				and time.time() - gameState.blockedSlave[slaveID] > 2.5:
			gameState.blockedSlave[slaveID] = 0.0
			slave: Slave | None = STR.GetSlave(slaveID)
			if slave:
				slave.SendSettingUpdateByName("__RGB", 0x0000FF)


if __name__ == "__main__":

	portList = GetPortList()

	#sound init
	mx.init(channels=1)

	global chan
	chan = mx.Channel(0)

	global sound
	sound = GameSound()

	display = TKDisplay()

	STR = Settingator(display)
	
	STR.AddToLayout(
			LayoutElement(
				IDP_COLUMN,
				None,
				"Control",
				children=[
					LayoutElement(
						IDP_BUTTON,
						None,
						"Reset Buzzer",
						callback=resetBuzzerFunc
					),
					LayoutElement(
						IDP_BUTTON,
						None,
						"Activate Buzzer",
						callback=activateBuzzerFunc
					),
					LayoutElement(
						IDP_BUTTON,
						None,
						"Validate",
						callback=validateQuestionFunc
					),
					LayoutElement(
						IDP_BUTTON,
						None,
						"Invalidate",
						callback=invalidateQuestionFunc
					)
				]
			)
		)

	STR.AddToLayout(
			LayoutElement(
				IDP_COLUMN,
				None,
				"Rules",
				children=[
					punishBuzzBeforeDingCheck,
					separateResetAndActivateCheck,
					gunForValidationCheck,
					gunForInvalidationCheck,
					gunForTooEarlyBuzzCheck
				]
			)
		)

	STR.AddToLayout(
			LayoutElement(
				IDP_COLUMN,
				None,
				"Player",
				children=[
					LayoutElement(
						IDP_FRAME,
						None,
						"",
						stick='w',
						children=[
							LayoutElement(
								IDP_TEXT,
								"Player Count: ",
								""
								),
							playerCount
							]
						),
					playerLayout
					]
				)
		)

	resetPlayerCount(2)

	STR.AddNotifCallback(BUZZ_BUTTON, buzzButton)

	while display.IsRunning():
		STR.Update()
		checkBlockedSlave()
