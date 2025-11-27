from Setting import *
from Communicator import ICTR
from Message import *
from Display import *
import queue
import time
import threading

def mac_to_str(mac: bytearray | bytes) -> str:
	return ':'.join(f'{b:02X}' for b in mac)

class LinkType(Enum):
	ESP_NOW = 0x00
	UNKNOWN = 0xFF

class Settingator:
	def __init__(self, ctr:ICTR, display:IDisplay) -> None:
		self.__communicator = ctr
		self.__slaveSettings = dict()
		self.__slaves = dict()
		self.__shouldUpdateDisplayLayout = False
		self.__shouldUpdateSetting = None
		self.__notifCallback = dict()
		self.__initCallback:callable = None
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
		mainLayout.AppendElement(self.__linkInfoLayout)
		leftLayout.AppendElement(self.__layout)
		leftLayout.AppendElement(self.__slaveLayout)

		self.__functionQueue = queue.Queue()

		return
	
	def GetSlave(self, slaveID:int):
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

			msg:Message = self.__communicator.Read()

			if msg.GetType() == MessageType.SETTING_INIT.value:
				self.__ParseSettingInit(msg.GetByteArray())

			elif msg.GetType() == MessageType.SETTING_UPDATE.value:
				ref, value, slaveID = msg.ExtractSettingUpdate()

				if slaveID in self.__slaveSettings:
					if ref in self.__slaveSettings[slaveID]:
						setting = self.__slaveSettings[slaveID][ref]
						setting.SetBinaryValue(value)
						self.__shouldUpdateSetting = setting

			elif msg.GetType() == MessageType.NOTIF.value:
				notifByte, slaveID = msg.ExtractNotif()

				if notifByte in self.__notifCallback:
					self.__notifCallback[notifByte](slaveID)

			elif msg.GetType() == MessageType.SLAVE_ID_REQUEST.value:
				self.SendInitRequest(self.__initCallback)
				print("Slave request recved")

			elif msg.GetType() == MessageType.LINK_INFO.value:
				print("Link Info received")				
				self.__treatLinkInfoMsg(msg.GetByteArray())


			self.__communicator.Flush()

		self.__updateEspNowLinkInf()

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
		
		type = MessageType.ESP_NOW_INIT_WITH_SSID.value
		buffer = bytearray()
		buffer.append(MessageControlFrame.START.value)
		buffer.append(0x00)
		buffer.append(0x00)
		buffer.append(slaveID)
		buffer.append(type)
		buffer += slaveName
		buffer.append(MessageControlFrame.END.value)
		size = buffer.__len__()
		buffer[1] = size >> 8
		buffer[2] = size

		bridgeInitRequest = Message(buffer)
		self.__communicator.Write(bridgeInitRequest)

	def SendInitRequest(self, callbackFunction:callable = None, slaveID = 0) -> None:
		self.__initCallback = callbackFunction

		type = MessageType.INIT_REQUEST.value
		buffer = bytearray()
		buffer.append(MessageControlFrame.START.value)
		buffer.append(0x00)
		buffer.append(0x07)

		if slaveID == 0:
			buffer.append(self.__slaveIDCount)
			self.__slaveIDCount += 1
		else:
			buffer.append(slaveID)

		buffer.append(MessageType.INIT_REQUEST.value)
		buffer.append(0x00)
		buffer.append(MessageControlFrame.END.value)

		initRequest = Message(buffer)
		self.__communicator.Write(initRequest)

	def BridgeStartInitBroadcasted(self, callbackFunction:callable = None) -> None:

		self.__initCallback = callbackFunction

		type = MessageType.ESP_NOW_START_INIT_BROADCASTED_SLAVE.value
		buffer = bytearray()
		buffer.append(MessageControlFrame.START.value)
		buffer.append(0x00)
		buffer.append(0x06)
		buffer.append(0x00)
		buffer.append(type)
		buffer.append(MessageControlFrame.END.value)

		message = Message(buffer)
		self.__communicator.Write(message)

	def BridgeStopInitBroadcasted(self) -> None:

		self.__initCallback = None

		type = MessageType.ESP_NOW_STOP_INIT_BROADCASTED_SLAVE.value
		buffer = bytearray()
		buffer.append(MessageControlFrame.START.value)
		buffer.append(0x00)
		buffer.append(0x06)
		buffer.append(0x00)
		buffer.append(type)
		buffer.append(MessageControlFrame.END.value)

		message = Message(buffer)
		self.__communicator.Write(message)

	def BridgeReInitSlaves(self) -> None:

		self.__initCallback = None

		type = MessageType.BRIDGE_REINIT_SLAVES.value
		buffer = bytearray()
		buffer.append(MessageControlFrame.START.value)
		buffer.append(0x00)
		buffer.append(0x06)
		buffer.append(0x00)
		buffer.append(type)
		buffer.append(MessageControlFrame.END.value)

		message = Message(buffer)
		self.__communicator.Write(message)

	def __ParseSettingInit(self, buffer:bytearray) -> bool:
		isValid = True

		slaveID = buffer[3]
		if not slaveID in self.__slaveSettings:
			self.__slaveSettings[slaveID] = dict()
		
		nbSetting = buffer[5]

		msgIndex = 6
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

				layoutElement:LayoutElement
				if settingType == SettingType.SLIDER.value:
					layoutElement = LayoutElement(IDP_SLIDER, setting.GetName())
					slaveLayout.AppendElement(layoutElement)
				
				elif settingType == SettingType.TRIGGER.value:
					layoutElement = LayoutElement(IDP_BUTTON, setting.GetValue(), setting.GetName(), callback=lambda value, setting=setting : self.SendUpdateSetting(setting, value))
					slaveLayout.AppendElement(layoutElement)

				elif settingType == SettingType.SWITCH.value or \
					settingType == SettingType.BOOL.value:
					layoutElement = LayoutElement(IDP_CHECK, setting.GetValue(), setting.GetName(), callback=lambda value, setting=setting : self.SendUpdateSetting(setting, value))
					slaveLayout.AppendElement(layoutElement)

				elif settingType == SettingType.FLOAT.value or\
					settingType == SettingType.UINT8.value or \
					settingType == SettingType.UINT16.value or \
					settingType == SettingType.UINT32.value or \
					settingType == SettingType.INT8.value or \
					settingType == SettingType.INT16.value or \
					settingType == SettingType.INT32.value or \
					settingType == SettingType.CUSTOM_FLOAT.value:
					slaveLayout.AppendElement(LayoutElement(IDP_TEXT, setting.GetName(), setting.GetName()))

					layoutElement = LayoutElement(IDP_INPUT, setting.GetValue(), setting.GetName(), callback=lambda value, setting=setting : self.SendUpdateSetting(setting, value))
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

		self.__slaveSettings[slaveID][ref] = Setting(ref, slaveID, name, settingType, value)
		
		msgIndex += nameLen + 1

		return msgIndex

	def __updateEspNowLinkInf(self):
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

							peerDict["layout"].UpdateValue(bridgeMac + "	<->    " + peerMac + "\n" +
											   str(peerDict["bridgeRssi"]) + "\t" +
											   str(peerDict["bridgeNoiseFloor"]) + "\t" +
											   str(peerDict["bridgeDeltaMs"]) + "\t" +
											   str(peerDict["peerRssi"]) + "\t" +
											   str(peerDict["peerNoiseFloor"]) + "\t" +
											   str(peerDict["peerDeltaMs"]))


							bridgeSNR = peerDict["bridgeRssi"] - peerDict["bridgeNoiseFloor"]
							peerSNR = peerDict["peerRssi"] - peerDict["peerNoiseFloor"]

							if	(peerDict["bridgeDeltaMs"] > 12500 or peerDict["peerDeltaMs"] > 12500):
								if peerDict["color"] != "grey":
									peerDict["layout"].GetIElement().SetBGColor("#B9B9B9")
									peerDict["color"] = "greu"

							elif (bridgeSNR <= 10 or peerSNR <= 10) :
								if peerDict["color"] != "red":
									peerDict["layout"].GetIElement().SetBGColor("#FF5050")
									peerDict["color"] = "red"

							elif (bridgeSNR <= 15 or peerSNR <= 15):
								if peerDict["color"] != "orange":
									peerDict["layout"].GetIElement().SetBGColor("#FFD476")
									peerDict["color"] = "orange"

							elif (bridgeSNR <= 25 or peerSNR <= 25):
								if peerDict["color"] != "green":
									peerDict["layout"].GetIElement().SetBGColor("#00FF00")
									peerDict["color"] = "green"

							elif (bridgeSNR > 25 or peerSNR > 25):
								if peerDict["color"] != "blue":
									peerDict["layout"].GetIElement().SetBGColor("#00FFFF")
									peerDict["color"] = "blue"





	def __treatLinkInfoMsg(self, buffer:bytearray):
		nbPeer = buffer[5]
		bridgeMac:str = mac_to_str(buffer[6:12])

		if not self.__linkInfo:
			self.__linkInfo = dict()

		if not bridgeMac in self.__linkInfo:
			self.__linkInfo[bridgeMac] = dict()

		self.__linkInfo[bridgeMac]["nbPeer"] = nbPeer

		index = 12
		for i in range(0, nbPeer):
			peerInfoSize = buffer[index]

			if peerInfoSize >= 3:
				slaveID = buffer[index + 1]
				linkType = buffer[index + 2]

				match linkType:
					case LinkType.ESP_NOW.value:

						peerMac = mac_to_str(buffer[index + 3: index + 9])

						if not peerMac in self.__linkInfo[bridgeMac]:
							self.__linkInfo[bridgeMac][peerMac] = dict(layout=LayoutElement(IDP_TEXT, "no_data"), color=None)
							self.__linkInfoLayout.AppendElement(self.__linkInfo[bridgeMac][peerMac]["layout"])

						peerDict = self.__linkInfo[bridgeMac][peerMac]

						peerDict["bridgeRssi"], len = GetInt8ValueFromBuffer(buffer[index + 9:])
						peerDict["bridgeNoiseFloor"], len = GetInt8ValueFromBuffer(buffer[index + 10:])
						peerDict["bridgeDeltaMs"], len = GetUInt32ValueFromBuffer(buffer[index + 11:])

						peerDict["peerRssi"], len = GetInt8ValueFromBuffer(buffer[index + 15:])
						peerDict["peerNoiseFloor"], len = GetInt8ValueFromBuffer(buffer[index + 16:])
						peerDict["peerDeltaMs"], len = GetUInt32ValueFromBuffer(buffer[index + 18:])

						peerDict["layout"].UpdateValue(bridgeMac + "	<->    " + peerMac + "\n" +
											   str(peerDict["bridgeRssi"]) + "\t" +
											   str(peerDict["bridgeNoiseFloor"]) + "\t" +
											   str(peerDict["bridgeDeltaMs"]) + "\t" +
											   str(peerDict["peerRssi"]) + "\t" +
											   str(peerDict["peerNoiseFloor"]) + "\t" +
											   str(peerDict["peerDeltaMs"]))
					case _:
						pass


	def SendUpdateSetting(self, setting:Setting, value = None) -> None:
		if threading.current_thread().name != "MainThread":
			self.PutFunctionToQueue(self.SendUpdateSetting, (setting, value))
			return
		
		if setting != None:
			if value != None:
				setting.SetValue(value)

			type = MessageType.SETTING_UPDATE.value
			buffer = bytearray()
			buffer.append(MessageControlFrame.START.value)
			buffer.append(0x00)
			buffer.append(0x00)
			buffer.append(setting.GetSlaveID())
			buffer.append(type)
			buffer.append(setting.GetRef())

			setting.AppendValueToBuffer(buffer)
			
			buffer.append(MessageControlFrame.END.value)
			size = buffer.__len__()
			buffer[1] = size >> 8
			buffer[2] = size

			self.__communicator.Write(Message(buffer))

	def SendMultiUpdateSetting(self, settingValue:list) -> None:
		if threading.current_thread().name != "MainThread":
			self.PutFunctionToQueue(self.SendUpdateSetting, (settingValue))
			return
		
		if settingValue != None:

			type = MessageType.SETTING_UPDATE.value
			buffer = bytearray()
			buffer.append(MessageControlFrame.START.value)
			buffer.append(0x00)
			buffer.append(0x00)
			buffer.append(0x00)
			buffer.append(type)

			for setting, value in settingValue:

				if setting != None:
					if value != None:
						setting.SetValue(value)

					buffer[3] = setting.GetSlaveID()

					buffer.append(setting.GetRef())

					setting.AppendValueToBuffer(buffer)

			buffer.append(MessageControlFrame.END.value)
			size = buffer.__len__()
			buffer[1] = size >> 8
			buffer[2] = size

			self.__communicator.Write(Message(buffer))

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
		buffer.append(MessageType.ESP_NOW_CONFIG_DIRECT_NOTF.value)
		buffer.append(dstSlaveID)
		buffer.append(notifByte)
		buffer.append(MessageControlFrame.END.value)

		self.__communicator.Write(Message(buffer))

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
			buffer.append(MessageType.ESP_NOW_CONFIG_DIRECT_SETTING_UPDATE.value)
			buffer.append(dstSlaveID)
			buffer.append(settingRef)
			buffer.append(setting.GetValueLen())
			buffer.append(MessageControlFrame.END.value)

			self.__communicator.Write(Message(buffer))

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

		self.__communicator.Write(Message(buffer))

	def RemoveDirectNotifConfig(self, srcSlaveID:int, dstSlaveID:int, notifByte:int) -> None:
		self.RemoveDirectMessageConfig(srcSlaveID, dstSlaveID, notifByte, MessageType.ESP_NOW_REMOVE_DIRECT_NOTIF_CONFIG.value)

	def RemoveDirectSettingUpdateConfig(self, srcSlaveID:int, dstSlave:int, settingRef:int) -> None:
		self.RemoveDirectMessageConfig(srcSlaveID, dstSlave, settingRef, MessageType.ESP_NOW_REMOVE_DIRECT_SETTING_UPDATE_CONFIG.value)

	def AddToLayout(self, layoutElement:LayoutElement) -> None:
		self.__layout.AppendElement(layoutElement)

	def RemoveFromLayout(self, layoutElement:LayoutElement) -> None:
		self.__layout.RemoveElement(layoutElement)

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
