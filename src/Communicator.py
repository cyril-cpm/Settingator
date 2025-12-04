from abc import ABC, abstractmethod
from typing import Type
from Setting import *
from Message import *
from collections import deque

class ISerial():
	def read(self) -> bytearray:
		pass

	def write(self, data:bytearray) -> None:
		pass

	def available(self) -> int:
		pass

class ICTR(ABC):
	def __init__(self) -> None:
		self.__receivedMessage = deque()
		self._rawText = ""

	def Available(self) -> int:
		self.Update()
		return self.__receivedMessage.__len__()
	
	def Write(self, message:Message) -> int:
		pass

	def Read(self) -> Message:
		return self.__receivedMessage[0]
	
	def Flush(self) -> None:
		self.__receivedMessage.popleft()
		return
	
	def Update(self) -> None:
		pass

	def GetBoxSize(self) -> int:
		return self.__receivedMessage.__len__()
	
	def _receive(self, message:Message) -> None:
		self.__receivedMessage.append(message)
		
		print("**")
		print(message.GetByteArray())
		print("**")
		return

	def GetRawText(self) -> str|None:
		if self._rawText == "":
			rawText = None
		else:
			rawText = self._rawText

		self._rawText = ""

		return rawText

		
