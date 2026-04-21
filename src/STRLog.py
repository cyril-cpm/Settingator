from gc import callbacks
from Display import *
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
				"SrcID",
				"DstID",
				"Type",
				"TimeStamp"
				]

		super().__init__(
				name="Message Log",
				callback=self.Details,
				stick=stick,
				columns=columns,
				)

		self.__logs = []

		self.__popupLayout = LayoutElement(IDP_FRAME, None, "MessageDetails", children=[
			LayoutElement(IDP_BUTTON, None, "Bouton")
			])

		self.__popup = PopupElement("Details", [self.__popupLayout]) 
		self.AppendElement(self.__popup)

	def Details(self, v) -> None:
		print("Details")
		index = int(self.GetIElement().GetFocusedElement())

		print(self.__logs[index][0].GetByteArray())

		self.__popup.SetVisible(True)

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
				"SrcID": message.GetSrcID(),
				"DstID": message.GetDstID(),
				"Type": message.GetType().name,
				"TimeStamp": currentTimeStr
				}

			self.AddEntry(entry)

			self.__logs.append((message, currentTime))
			self.SetModified(True)

