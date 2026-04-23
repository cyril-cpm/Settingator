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

		self.__messageML = LayoutElement(IDP_MULTILINE, width=47)
		self.__wayLabel = LayoutElement(IDP_TEXT)
		self.__sizeLabel = LayoutElement(IDP_TEXT)
		self.__srcLabel = LayoutElement(IDP_TEXT)
		self.__dstLabel = LayoutElement(IDP_TEXT)
		self.__typeLabel = LayoutElement(IDP_TEXT)
		self.__timestampLabel = LayoutElement(IDP_TEXT)

		self.__popupLayout = LayoutElement(IDP_FRAME, None, "MessageDetails", children=[
				LayoutElement(IDP_COLUMN, None, children=[
					self.__wayLabel,
					self.__sizeLabel,
					self.__srcLabel,
					self.__dstLabel,
					self.__typeLabel,
					self.__timestampLabel
				]),
				self.__messageML
			])

		self.__popup = PopupElement("Details", [self.__popupLayout]) 
		self.AppendElement(self.__popup)

	def Details(self, v=None, index=None) -> None:
		iElement = self.GetIElement()
		if not index:
			focused = iElement.GetFocusedElement()

			if focused != '':
				index = int(focused)

		if index is not None:
			timestamp = self.__logs[index][1]
			message:Message = self.__logs[index][0]
			way = self.__logs[index][2]

			self.__messageML.GetIElement().Reset()
			self.__messageML.GetIElement().Insert(None, message.GetByteArray().hex(' '))

			self.__wayLabel.UpdateValue(way)
			self.__sizeLabel.UpdateValue("LEN: " + str(message.GetLength()))
			self.__srcLabel.UpdateValue("SRC: " + str(message.GetSrcID()))
			self.__dstLabel.UpdateValue("DST: " + str(message.GetDstID()))
			self.__typeLabel.UpdateValue(message.GetType().name)
			self.__timestampLabel.UpdateValue(timestamp)

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

			self.__logs.append((message, currentTimeStr, way))
			self.SetModified(True)

