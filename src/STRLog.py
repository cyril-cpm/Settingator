from Display import ListBoxElement
from Message import MessageType, Message

import datetime

# def MessageTypeToStr(msgType:MessageType = MessageType.UNINITIALISED) -> str:
# 	if msgTYpe == MessageType.UNINITIALISED:
# 		return "UNINITIALISED"
# 	elif msgType == MessageType.SETTING_UPDATE:
# 		return "SETTING_UPDATE"

class STRMessgeLog(ListBoxElement):
	def __init__(self, stick="nsew") -> None:
		columns = [
				"Way",
				"Size",
				"SlaveID",
				"Type",
				"TimeStamp"
				]

		super().__init__(
				name="Message Log",
				callback="None",
				stick=stick,
				columns=columns
				)

	def Log(self, message:Message | None = None,
		 way:str|None = None) -> None:

		if message:
			if not way:
				way = "unknown"

			currentTime = datetime.datetime.now()

			currentTimeStr = currentTime.strftime("%H:%M:%S.%f")

			entry = {
				"Way": way,
				"Size": message.GetLength(),
				"SlaveID": message.GetSlaveID(),
				"Type": message.GetType().name,
				"TimeStamp": currentTimeStr
				}

			self.AddEntry(entry)

