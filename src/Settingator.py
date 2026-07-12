from STRLog import STRMessgeLog
from Setting import *
from Communicator import ICTR
from Message import *
from Display import *
import queue
import time
import threading
import traceback
from Log import Logger

def mac_to_str(mac: bytearray | bytes) -> str:
	return ':'.join(f'{b:02X}' for b in mac)

class LinkType(Enum):
	ESP_NOW = 0x00
	UART = 0x01
	LORA = 0x02
	UNKNOWN = 0xFF

class Settingator:
	def __init__(self, ctr:ICTR, display:IDisplay) -> None:
		self.__communicator = ctr
		self.__slaveSettings = dict()
		self.__slaves = dict()
		self.__shouldUpdateDisplayLayout = False
		self.__shouldUpdateSetting = None
		self.__notifCallback = dict()
		self.__initCallback:Callable|None = None
		self.__slaveIDCount:int = 1

		# Display Stuff
		self.__display = display
		self.__display.SetSlaveSettingsRef(self.__slaveSettings)
		self.__linkInfo = None
		self.__linkInfoLayout = LayoutElement(IDP_COLUMN, stick="e")
		self.__layout = LayoutElement(IDP_FRAME)
		self.__slaveLayout = LayoutElement(IDP_FRAME)

		leftLayout = LayoutElement(IDP_COLUMN)
		mainLayout = LayoutElement(IDP_FRAME)

		self.__display.AddLayout(mainLayout)

		mainLayout.AppendElement(leftLayout)
		self.__slaveLayout.AppendElement(self.__linkInfoLayout)

		leftLayout.AppendElement(self.__layout)
		leftLayout.AppendElement(self.__slaveLayout)

		#LOG LAYOUT STUFF

		logLayout = LayoutElement(IDP_FRAME)
		leftLayout.AppendElement(logLayout)

		self.__generalLog = LogElement()
		logLayout.AppendElement(self.__generalLog)

		self.__msgLogger:STRMessgeLog = STRMessgeLog()

		logLayout.AppendElement(self.__msgLogger)

		Logger.AddCallback(self.__generalLog.Log)

		#################

		self.__functionQueue = queue.Queue()

		return
	
	def GetSlave(self, slaveID:int) -> Slave | None:
		if slaveID in self.__slaves:
			return self.__slaves[slaveID]
		return None
	
	def RemoveSlaveLayout(self) -> None:
		self.__slaveLayout.SetVisible(False)

	def DisplaySlaveLayout(self) -> None:
		self.__slaveLayout.SetVisible(True)
	
	def GetSlaves(self):
		return self.__slaves
	
	def GetSlaveWithSetting(self, settingName):
		for i in self.__slaves:
			slave:Slave = self.__slaves[i]
			if slave.GetSettingByName(settingName) != None:
				return slave

	def PutFunctionToQueue(self, f, args):
		self.__functionQueue.put((f, args))

	def Update(self) -> None:

		if self.__communicator.Available():
			rawText = self.__communicator.GetRawText()

			# if rawText:
			# 	Logger.Log(rawText, "CTR", "CTR_RAW_TEXT")

			msg:Message = self.Read()

			if msg.GetType() == MessageType.SETTING_INIT:
				self.__ParseSettingInit(msg.GetByteArray())

			elif msg.GetType() == MessageType.SETTING_UPDATE:
				ref, value, slaveID = msg.ExtractSettingUpdate()

				if slaveID in self.__slaveSettings:
					if ref in self.__slaveSettings[slaveID]:
						setting = self.__slaveSettings[slaveID][ref]
						setting.SetBinaryValue(value)
						self.__shouldUpdateSetting = setting

			elif msg.GetType() == MessageType.NOTIF:
				notifByte, slaveID = msg.ExtractNotif()

				if notifByte in self.__notifCallback:
					self.__notifCallback[notifByte](slaveID)

			elif msg.GetType() == MessageType.SLAVE_ID_REQUEST:
				self.SendInitRequest(self.__initCallback)
				print("Slave request recved")

			elif msg.GetType() == MessageType.LINK_INFO:
				print("Link Info received")
				# Garde-fou : une trame LinkInfo malformee ne doit pas tuer
				# toute la GUI (la boucle principale n'a pas de try/except).
				try:
					self.__treatLinkInfoMsg(msg.GetByteArray())
				except Exception:
					Logger.Log("Exception dans __treatLinkInfoMsg", "LINK", "ERROR")
					traceback.print_exc()


			self.__communicator.Flush()

		try:
			self.__updateLinkInfo()
		except Exception:
			Logger.Log("Exception dans __updateLinkInfo", "LINK", "ERROR")
			traceback.print_exc()

		self.__display.Update()
		
		while True:
			try:
				f, args = self.__functionQueue.get_nowait()
				f(*args)
			except queue.Empty:
				break

		if self.__shouldUpdateDisplayLayout:
			self.__display.UpdateLayout()
			self.__shouldUpdateDisplayLayout = False

		if self.__shouldUpdateSetting != None:
			self.__display.UpdateSetting(self.__shouldUpdateSetting)
			self.__shouldUpdateSetting = None

		return
	
	def SendBridgeInitRequest(self, slaveID:int, slaveName:bytearray, callbackFunction:callable = None, expectedSlaveNumber:int = 1) -> None: #deprecated
		
		self.__initCallback = callbackFunction
		
		type = MessageType.ESP_NOW_INIT_WITH_SSID
		buffer = bytearray()
		buffer.append(MessageControlFrame.START.value)
		buffer.append(0x00)
		buffer.append(0x00)
		buffer.append(slaveID)
		buffer.append(type.value)
		buffer += slaveName
		buffer.append(MessageControlFrame.END.value)
		size = buffer.__len__()
		buffer[1] = size >> 8
		buffer[2] = size

		bridgeInitRequest = Message(buffer)
		self.Write(bridgeInitRequest)

	def SendInitRequest(self, callbackFunction:callable = None, slaveID = 0) -> None:
		self.__initCallback = callbackFunction

		type = MessageType.INIT_REQUEST
		buffer = bytearray()
		buffer.append(MessageControlFrame.START.value)
		buffer.append(0x00)
		buffer.append(0x08)

		buffer.append(0x00)

		if slaveID == 0:
			buffer.append(self.__slaveIDCount)
			self.__slaveIDCount += 1
		else:
			buffer.append(slaveID)


		buffer.append(type.value)
		buffer.append(0x00)
		buffer.append(MessageControlFrame.END.value)

		initRequest = Message(buffer)
		self.Write(initRequest)

	def BridgeStartInitBroadcasted(self, callbackFunction:callable = None) -> None:

		self.__initCallback = callbackFunction

		type = MessageType.LINK_START_INIT_BROADCASTED_SLAVE
		buffer = bytearray()
		buffer.append(MessageControlFrame.START.value)
		buffer.append(0x00)
		buffer.append(0x07)
		buffer.append(0x00)
		buffer.append(0x00)
		buffer.append(type.value)
		buffer.append(MessageControlFrame.END.value)

		message = Message(buffer)
		self.Write(message)

	def BridgeStopInitBroadcasted(self) -> None:

		self.__initCallback = None

		type = MessageType.LINK_STOP_INIT_BROADCASTED_SLAVE
		buffer = bytearray()
		buffer.append(MessageControlFrame.START.value)
		buffer.append(0x00)
		buffer.append(0x07)
		buffer.append(0x00)
		buffer.append(0x00)
		buffer.append(type.value)
		buffer.append(MessageControlFrame.END.value)

		message = Message(buffer)
		self.Write(message)

	def BridgeReInitSlaves(self) -> None:

		self.__initCallback = None

		type = MessageType.BRIDGE_REINIT_SLAVES
		buffer = bytearray()
		buffer.append(MessageControlFrame.START.value)
		buffer.append(0x00)
		buffer.append(0x06)
		buffer.append(0x00)
		buffer.append(type.value)
		buffer.append(MessageControlFrame.END.value)

		message = Message(buffer)
		self.Write(message)

	def __ParseSettingInit(self, buffer:bytearray) -> bool:
		isValid = True

		slaveID = buffer[3]
		if not slaveID in self.__slaveSettings:
			self.__slaveSettings[slaveID] = dict()
		
		nbSetting = buffer[6]

		msgIndex = 7
		loopIndex = 0

		while((loopIndex < nbSetting) and isValid):
			msgIndex = self.__ParseSetting(buffer, msgIndex, slaveID)
			if (msgIndex < 0):
				isValid = False

			loopIndex += 1

		if (loopIndex != nbSetting):
			isValid = False

		if (msgIndex != (buffer.__len__() - 1) and buffer[msgIndex] != MessageControlFrame.END.value):
			isValid = False
		
		self.__shouldUpdateDisplayLayout = True

		if not slaveID in self.__slaves:
			self.__slaves[slaveID] = Slave(self, slaveID, self.__slaveSettings[slaveID])

			slaveLayout = LayoutElement(IDP_COLUMN, None, "Slave "+str(slaveID))

			for settingRef in self.__slaveSettings[slaveID]:
				setting:Setting = self.__slaveSettings[slaveID][settingRef]
				settingType = setting.GetType()
				settingName = setting.GetName()

				layoutElement:LayoutElement
				if settingType == SettingType.SLIDER.value:
					layoutElement = LayoutElement(IDP_SLIDER, setting.GetName())
					slaveLayout.AppendElement(layoutElement)
				
				elif settingType == SettingType.TRIGGER.value:
					layoutElement = LayoutElement(
							IDP_BUTTON,
							setting.GetValue(),
							setting.GetName(),
							callback=lambda value, setting=setting : 
								self.SendUpdateSetting(setting, value)
						)
					slaveLayout.AppendElement(layoutElement)

				elif settingType == SettingType.SWITCH.value or \
					settingType == SettingType.BOOL.value:
					layoutElement = LayoutElement(
							IDP_CHECK,
							setting.GetValue(),
							setting.GetName(),
							callback=lambda value, setting=setting :
								self.SendUpdateSetting(setting, value)
						)
					slaveLayout.AppendElement(layoutElement)

				elif settingType == SettingType.FLOAT.value or\
					settingType == SettingType.UINT8.value or \
					settingType == SettingType.UINT16.value or \
					settingType == SettingType.UINT32.value or \
					settingType == SettingType.INT8.value or \
					settingType == SettingType.INT16.value or \
					settingType == SettingType.INT32.value or \
					settingType == SettingType.CUSTOM_FLOAT.value:
					slaveLayout.AppendElement(
							LayoutElement(IDP_TEXT, setting.GetName(), setting.GetName())
						)

					if settingName == "__RGB":
						layoutElement = LayoutElement(
								IDP_INPUT,
								hex(setting.GetValue()),
								setting.GetName(),
								callback = lambda value :
									self.SendUpdateSetting(setting, int(value, 16))
							)

					else:
						layoutElement = LayoutElement(
								IDP_INPUT,
								setting.GetValue(),
								setting.GetName(),
								callback=lambda value, setting=setting :
									self.SendUpdateSetting(setting, value)
							)

					slaveLayout.AppendElement(layoutElement)

				else:
					layoutElement = LayoutElement(IDP_TEXT, "Unhandled type : " + str(settingType))
					slaveLayout.AppendElement(layoutElement)

				setting.SetLayoutElement(layoutElement)
				

			self.__slaveLayout.AppendElement(slaveLayout)
			self.__display.UpdateLayout()

		if self.__initCallback != None:
			self.__initCallback(self.__slaves[slaveID])

		return isValid

	def __ParseSetting(self, buffer:bytearray, msgIndex:int, slaveID:int) -> int:
		msgSize = buffer.__len__()

		if (msgIndex >= msgSize):
			return -1

		ref = buffer[msgIndex]

		msgIndex += 1
		if (msgIndex >= msgSize):
			return -1

		settingType = buffer[msgIndex]
		
		msgIndex += 1  
		if (msgIndex >= msgSize):
			return -1

		valueLen = buffer[msgIndex]
		value = GetBytes(buffer, msgIndex)

		msgIndex += valueLen + 1
		
		if (msgIndex >= msgSize):
			return -1

		nameLen = buffer[msgIndex]

		if ((msgIndex + nameLen) >= msgSize):
			return -1

		name = GetString(buffer, msgIndex)

		if ref not in self.__slaveSettings[slaveID]:
			self.__slaveSettings[slaveID][ref] = Setting(ref, slaveID, name, settingType, value)
		
		msgIndex += nameLen + 1

		return msgIndex

	# ------------------------------------------------------------------ #
	#  Affichage des liaisons (LinkInfo)                                  #
	# ------------------------------------------------------------------ #

	def __linkModeName(self, linkType:int) -> str:
		if linkType == LinkType.ESP_NOW.value:
			return "ESP-NOW"
		elif linkType == LinkType.LORA.value:
			return "LoRa"
		elif linkType == LinkType.UART.value:
			return "UART"
		return "?"

	def __snrColor(self, snr:int) -> str:
		# Code couleur selon la qualité du lien (SNR = RSSI - noise floor)
		if snr <= 10:
			return "#FF5050"		# rouge   : critique
		elif snr <= 15:
			return "#FFD476"		# orange  : faible
		elif snr <= 25:
			return "#00FF00"		# vert    : correct
		return "#00FFFF"			# bleu    : excellent

	def __setLabelBGColor(self, labelElement, colorHex):
		# Le style n'existe qu'une fois l'element rendu par le display :
		# on ignore silencieusement tant que l'IElement n'est pas construit.
		iel = labelElement.GetIElement()
		if iel:
			iel.SetBGColor(colorHex)

	def __buildPeerCard(self, bridgeMac:str, peerMac:str, slaveID:int, linkType:int) -> dict:
		# Construit la "carte" d'un peer et memorise les references des widgets
		# a rafraichir. Les donnees numeriques sont stockees dans le meme dict.
		peerDict = dict(
				color=None, bridgeColor=None, peerColor=None,
				slaveID=slaveID, linkType=linkType,
				bridgeRssi=0, bridgeNoiseFloor=0, bridgeDeltaMs=0,
				peerRssi=0, peerNoiseFloor=0, peerDeltaMs=0)

		card = LayoutElement(IDP_COLUMN, None, "Slave " + str(slaveID))

		# --- En-tete : adresses MAC des deux extremites du lien ---
		header = LayoutElement(IDP_COLUMN, None, "Liaison")

		bridgeRow = LayoutElement(IDP_FRAME)
		bridgeRow.AppendElement(LayoutElement(IDP_TEXT, "Bridge", stick="w"))
		bridgeRow.AppendElement(LayoutElement(IDP_TEXT, bridgeMac, stick="w"))

		peerRow = LayoutElement(IDP_FRAME)
		peerRow.AppendElement(LayoutElement(IDP_TEXT, "Peer", stick="w"))
		peerRow.AppendElement(LayoutElement(IDP_TEXT, peerMac + "  (id " + str(slaveID) + ")", stick="w"))

		header.AppendElement(bridgeRow)
		header.AppendElement(peerRow)
		card.AppendElement(header)

		# --- Metriques radio : une colonne par extremite du lien ---
		metrics = LayoutElement(IDP_FRAME)

		bridgeBox = LayoutElement(IDP_COLUMN, None, "Cote Bridge")
		peerDict["bridgeRssiLabel"]  = LayoutElement(IDP_TEXT, "", stick="w")
		peerDict["bridgeFloorLabel"] = LayoutElement(IDP_TEXT, "", stick="w")
		peerDict["bridgeSnrLabel"]   = LayoutElement(IDP_TEXT, "", stick="w")
		peerDict["bridgeAgeLabel"]   = LayoutElement(IDP_TEXT, "", stick="w")
		for key in ("bridgeRssiLabel", "bridgeFloorLabel", "bridgeSnrLabel", "bridgeAgeLabel"):
			bridgeBox.AppendElement(peerDict[key])

		peerBox = LayoutElement(IDP_COLUMN, None, "Cote Peer")
		peerDict["peerRssiLabel"]  = LayoutElement(IDP_TEXT, "", stick="w")
		peerDict["peerFloorLabel"] = LayoutElement(IDP_TEXT, "", stick="w")
		peerDict["peerSnrLabel"]   = LayoutElement(IDP_TEXT, "", stick="w")
		peerDict["peerAgeLabel"]   = LayoutElement(IDP_TEXT, "", stick="w")
		for key in ("peerRssiLabel", "peerFloorLabel", "peerSnrLabel", "peerAgeLabel"):
			peerBox.AppendElement(peerDict[key])

		metrics.AppendElement(bridgeBox)
		metrics.AppendElement(peerBox)
		card.AppendElement(metrics)

		# --- Barre "mode de communication" : etat courant + action ---
		modeRow = LayoutElement(IDP_FRAME)
		peerDict["modeLabel"] = LayoutElement(IDP_TEXT, "Lien : " + self.__linkModeName(linkType), stick="w")
		modeRow.AppendElement(peerDict["modeLabel"])

		# Espace cliquable pour basculer le mode de communication a la volee.
		# IDP_BUTTON convient. Son libelle (text=name) est statique : l'etat
		# courant est donc affiche dans "modeLabel" ci-dessus (mis a jour
		# dynamiquement a chaque trame LinkInfo et a chaque bascule).
		modeButton = LayoutElement(
				IDP_BUTTON,
				None,
				"\u21C4 Changer de mode",
				callback=lambda value, bm=bridgeMac, pd=peerDict:
					self.__toggleLinkMode(bm, pd)
			)
		modeRow.AppendElement(modeButton)
		card.AppendElement(modeRow)

		peerDict["card"] = card
		return peerDict

	def __refreshPeerMetrics(self, peerDict:dict):
		# Pousse les valeurs courantes dans les labels et renvoie les deux SNR.
		bridgeSNR = peerDict["bridgeRssi"] - peerDict["bridgeNoiseFloor"]
		peerSNR   = peerDict["peerRssi"] - peerDict["peerNoiseFloor"]

		peerDict["bridgeRssiLabel"].UpdateValue("RSSI   " + str(peerDict["bridgeRssi"]) + " dBm")
		peerDict["bridgeFloorLabel"].UpdateValue("Floor  " + str(peerDict["bridgeNoiseFloor"]) + " dBm")
		peerDict["bridgeSnrLabel"].UpdateValue("SNR    " + str(bridgeSNR) + " dB")
		peerDict["bridgeAgeLabel"].UpdateValue("Age    " + str(peerDict["bridgeDeltaMs"]) + " ms")

		peerDict["peerRssiLabel"].UpdateValue("RSSI   " + str(peerDict["peerRssi"]) + " dBm")
		peerDict["peerFloorLabel"].UpdateValue("Floor  " + str(peerDict["peerNoiseFloor"]) + " dBm")
		peerDict["peerSnrLabel"].UpdateValue("SNR    " + str(peerSNR) + " dB")
		peerDict["peerAgeLabel"].UpdateValue("Age    " + str(peerDict["peerDeltaMs"]) + " ms")

		return bridgeSNR, peerSNR

	def __applyLinkColor(self, peerDict:dict, bridgeSNR:int, peerSNR:int):
		# Coloration par extremite (on voit ainsi quel cote decroche).
		# Lien fige (donnees trop vieilles) -> gris.
		stale = peerDict["bridgeDeltaMs"] > 12500 or peerDict["peerDeltaMs"] > 12500

		if stale:
			bridgeColor = peerColor = "#B9B9B9"
		else:
			bridgeColor = self.__snrColor(bridgeSNR)
			peerColor   = self.__snrColor(peerSNR)

		if peerDict.get("bridgeColor") != bridgeColor:
			self.__setLabelBGColor(peerDict["bridgeSnrLabel"], bridgeColor)
			peerDict["bridgeColor"] = bridgeColor

		if peerDict.get("peerColor") != peerColor:
			self.__setLabelBGColor(peerDict["peerSnrLabel"], peerColor)
			peerDict["peerColor"] = peerColor

	def __toggleLinkMode(self, bridgeMac:str, peerDict:dict):
		# Bascule optimiste ESP-NOW <-> LoRa. L'affichage sera de toute facon
		# recale sur le mode reellement rapporte par le bridge a la prochaine
		# trame LinkInfo (cf. __treatLinkInfoMsg).
		current = peerDict.get("linkType", LinkType.ESP_NOW.value)
		if current == LinkType.ESP_NOW.value:
			newLinkType = LinkType.LORA.value
		else:
			newLinkType = LinkType.ESP_NOW.value

		peerDict["linkType"] = newLinkType
		peerDict["modeLabel"].UpdateValue("Lien : " + self.__linkModeName(newLinkType))

		Logger.Log("Changement de mode demande pour slave " + str(peerDict.get("slaveID")) +
				" -> " + self.__linkModeName(newLinkType), "LINK", "INFO")

		self.__sendLinkModeChange(bridgeMac, peerDict.get("slaveID"), newLinkType)

	def __sendLinkModeChange(self, bridgeMac:str, slaveID:int, newLinkType:int):
		# SUGGESTION / TODO protocole :
		# Il n'existe pas encore de MessageType pour le changement de mode de lien.
		# Proposition : ajouter dans Message.py -> class MessageType :
		#     LINK_MODE_CHANGE = 0x60
		# puis emettre la trame :
		#     [START, sizeHi, sizeLo, slaveID, LINK_MODE_CHANGE, newLinkType, END]
		# Implementation prete a activer une fois l'opcode defini cote firmware :
		#
		# buffer = bytearray()
		# buffer.append(MessageControlFrame.START.value)
		# buffer.append(0x00)
		# buffer.append(0x00)
		# buffer.append(slaveID)
		# buffer.append(MessageType.LINK_MODE_CHANGE.value)
		# buffer.append(newLinkType)
		# buffer.append(MessageControlFrame.END.value)
		# size = len(buffer)
		# buffer[1] = size >> 8
		# buffer[2] = size & 0xFF
		# self.Write(Message(buffer))
		pass

	def __updateLinkInfo(self):
		if not self.__linkInfo:
			return

		currentTimeStamp = int(time.time() * 1000)

		if not "last_updated" in self.__linkInfo:
			self.__linkInfo["last_updated"] = currentTimeStamp

		diffTimeStamp = currentTimeStamp - self.__linkInfo["last_updated"]
		if diffTimeStamp > 500:
			self.__linkInfo["last_updated"] = currentTimeStamp

			for bridgeMac in self.__linkInfo:

				if bridgeMac != "last_updated":
					for peerMac in self.__linkInfo[bridgeMac]:

						if peerMac != "nbPeer":
							peerDict = self.__linkInfo[bridgeMac][peerMac]

							peerDict["bridgeDeltaMs"] = peerDict["bridgeDeltaMs"] + diffTimeStamp
							peerDict["peerDeltaMs"] = peerDict["peerDeltaMs"] + diffTimeStamp

							bridgeSNR, peerSNR = self.__refreshPeerMetrics(peerDict)
							self.__applyLinkColor(peerDict, bridgeSNR, peerSNR)

	def __treatLinkInfoMsg(self, buffer:bytearray):
		nbPeer = buffer[6]
		bridgeMac:str = mac_to_str(buffer[7:13])

		if not self.__linkInfo:
			self.__linkInfo = dict()

		if not bridgeMac in self.__linkInfo:
			self.__linkInfo[bridgeMac] = dict()

		self.__linkInfo[bridgeMac]["nbPeer"] = nbPeer

		index = 13
		for i in range(0, nbPeer):
			peerInfoSize = buffer[index]

			if peerInfoSize >= 3:
				slaveID = buffer[index + 1]
				peerMac = mac_to_str(buffer[index + 2: index + 8])
				linkType = buffer[index + 8]

				match linkType:
					case LinkType.ESP_NOW.value | LinkType.LORA.value:

						if not peerMac in self.__linkInfo[bridgeMac]:
							peerDict = self.__buildPeerCard(bridgeMac, peerMac, slaveID, linkType)
							self.__linkInfo[bridgeMac][peerMac] = peerDict
							self.__linkInfoLayout.AppendElement(peerDict["card"])

						peerDict = self.__linkInfo[bridgeMac][peerMac]

						peerDict["slaveID"] = slaveID
						peerDict["linkType"] = linkType
						peerDict["modeLabel"].UpdateValue("Lien : " + self.__linkModeName(linkType))

						peerDict["bridgeRssi"], _ = GetInt8ValueFromBuffer(buffer[index + 9:])
						peerDict["bridgeNoiseFloor"], _ = GetInt8ValueFromBuffer(buffer[index + 10:])
						peerDict["bridgeDeltaMs"], _ = GetUInt32ValueFromBuffer(buffer[index + 11:])

						peerDict["peerRssi"], _ = GetInt8ValueFromBuffer(buffer[index + 15:])
						peerDict["peerNoiseFloor"], _ = GetInt8ValueFromBuffer(buffer[index + 16:])
						peerDict["peerDeltaMs"], _ = GetUInt32ValueFromBuffer(buffer[index + 17:])

						self.__refreshPeerMetrics(peerDict)

					case _:
						pass

			index += peerInfoSize



	def SendUpdateSetting(self, setting:Setting, value = None) -> None:
		if threading.current_thread().name != "MainThread":
			self.PutFunctionToQueue(self.SendUpdateSetting, (setting, value))
			return
		
		if setting != None:
			if value != None:
				setting.SetValue(value)

			type = MessageType.SETTING_UPDATE
			buffer = bytearray()
			buffer.append(MessageControlFrame.START.value)
			buffer.append(0x00)
			buffer.append(0x00)
			buffer.append(0x00) # src slave ID
			buffer.append(setting.GetSlaveID()) # dst slave ID
			buffer.append(type.value)
			buffer.append(setting.GetRef())

			setting.AppendValueToBuffer(buffer)
			
			buffer.append(MessageControlFrame.END.value)
			size = buffer.__len__()
			buffer[1] = size >> 8
			buffer[2] = size

			self.Write(Message(buffer))

	def SendMultiUpdateSetting(self, settingValue:list) -> None:
		if threading.current_thread().name != "MainThread":
			self.PutFunctionToQueue(self.SendUpdateSetting, (settingValue))
			return
		
		if settingValue != None:

			type = MessageType.SETTING_UPDATE
			buffer = bytearray()
			buffer.append(MessageControlFrame.START.value)
			buffer.append(0x00)
			buffer.append(0x00)
			buffer.append(0x00)
			buffer.append(0x00)
			buffer.append(type.value)

			for setting, value in settingValue:

				if setting != None:
					if value != None:
						setting.SetValue(value)

					buffer[4] = setting.GetSlaveID()

					buffer.append(setting.GetRef())

					setting.AppendValueToBuffer(buffer)

			buffer.append(MessageControlFrame.END.value)
			size = buffer.__len__()
			buffer[1] = size >> 8
			buffer[2] = size

			self.Write(Message(buffer))

	def GetSlaveSettings(self) -> dict:
		return self.__slaveSettings
	
	def AddNotifCallback(self, notifByte:int, callback) -> None:
		self.__notifCallback[notifByte] = callback

	def RemoveNotifCallback(self, notifByte:int) -> None:
		None
		
	def ConfigDirectNotf(self, srcSlaveID:int, dstSlaveID:int, notifByte:int) -> None:
		buffer = bytearray()
		buffer.append(MessageControlFrame.START.value)
		buffer.append(0x00)
		buffer.append(0x08)
		buffer.append(srcSlaveID)
		buffer.append(MessageType.ESP_NOW_CONFIG_DIRECT_NOTF)
		buffer.append(dstSlaveID)
		buffer.append(notifByte)
		buffer.append(MessageControlFrame.END.value)

		self.Write(Message(buffer))

	def ConfigDirectSettingUpdate(self, srcSlaveID:int, dstSlaveID:int, settingRef) -> None:
		setting:Setting = None

		if dstSlaveID in self.__slaveSettings:
			if settingRef in self.__slaveSettings[dstSlaveID]:
				setting = self.__slaveSettings[dstSlaveID][settingRef]
			
			else:
				print("SettingRef " + str(settingRef) + " not found on Slave " + str(dstSlaveID))
		
		else:
			print("Slave " + str(dstSlaveID) + " not found")

		if setting != None:
			buffer = bytearray()
			buffer.append(MessageControlFrame.START.value)
			buffer.append(0x00)
			buffer.append(0x08)
			buffer.append(srcSlaveID)
			buffer.append(MessageType.ESP_NOW_CONFIG_DIRECT_SETTING_UPDATE)
			buffer.append(dstSlaveID)
			buffer.append(settingRef)
			buffer.append(setting.GetValueLen())
			buffer.append(MessageControlFrame.END.value)

			self.Write(Message(buffer))

	def RemoveDirectMessageConfig(self, srcSlaveID:int, dstSlaveID:int, configID:int, configType:int) -> None:
		buffer = bytearray()
		buffer.append(MessageControlFrame.START.value)
		buffer.append(0x00)
		buffer.append(0x08)
		buffer.append(srcSlaveID)
		buffer.append(configType)
		buffer.append(dstSlaveID)
		buffer.append(configID)
		buffer.append(MessageControlFrame.END.value)

		self.Write(Message(buffer))

	def RemoveDirectNotifConfig(self, srcSlaveID:int, dstSlaveID:int, notifByte:int) -> None:
		self.RemoveDirectMessageConfig(srcSlaveID, dstSlaveID, notifByte, MessageType.ESP_NOW_REMOVE_DIRECT_NOTIF_CONFIG)

	def RemoveDirectSettingUpdateConfig(self, srcSlaveID:int, dstSlave:int, settingRef:int) -> None:
		self.RemoveDirectMessageConfig(srcSlaveID, dstSlave, settingRef, MessageType.ESP_NOW_REMOVE_DIRECT_SETTING_UPDATE_CONFIG)

	def AddToLayout(self, layoutElement:LayoutElement) -> None:
		self.__layout.AppendElement(layoutElement)

	def RemoveFromLayout(self, layoutElement:LayoutElement) -> None:
		self.__layout.RemoveElement(layoutElement)

	def Log(self, text:str, typeLog:str, tag:str):
		if self.__generalLog:
			self.__generalLog.Log(text, typeLog)

	def Write(self, message:Message):
		if (self.__communicator):
			self.__msgLogger.Log(message, "OUT")
			self.__communicator.Write(message)
	
	def Read(self) -> Message:
		if (self.__communicator):
			message = self.__communicator.Read()
			self.__msgLogger.Log(message, "IN")
			return message
		
		return Message()

class Slave:
	def __init__(self, str:Settingator, slaveID:int, settings:dict) -> None:
		self.__ID = slaveID
		self.__settings = settings
		self.__str = str

	def GetSettingByRef(self, ref:int) -> Setting:
		return self.__settings[ref]

	def GetSettingByName(self, settingName:str) -> Setting:
		for setting in self.__settings:
			if self.__settings[setting].GetName() == settingName:
				return self.GetSettingByRef(setting)
		return None

	def SendSettingUpdateByRef(self, ref:int, value = None):
		self.__str.SendUpdateSetting(self.__settings[ref], value)

	def SendSettingUpdateByName(self, settingName:str, value = None):

		for setting in self.__settings:
			if self.__settings[setting].GetName() == settingName:
				self.SendSettingUpdateByRef(self.__settings[setting].GetRef(), value)
				break

	def SendSettingUpdatesByName(self, settings:list) -> None:
		setValue = []

		for nameValue in settings:
			name, value = nameValue
			setting = self.GetSettingByName(name)

			if setting:
				setValue.append((setting, value))

		self.__str.SendMultiUpdateSetting(setValue)

	def ConfigDiretNotif(self, target, notifByte:int):
		self.__str.ConfigDirectNotf(self.__ID, target.GetID(), notifByte)

	def ConfigDirectSettingUpdate(self, target, settingRef:int):
		self.__str.ConfigDirectSettingUpdate(self.__ID, target.GetID(), settingRef)

	def RemoveDirectSettingUpdateConfig(self, target, settingRef:int):
		self.__str.RemoveDirectSettingUpdateConfig(self.__ID, target.GetID(), settingRef)

	def GetID(self):
		return self.__ID

