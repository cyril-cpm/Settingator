from typing import Callable

class Logger:

	_callback:List = []

	@classmethod
	def AddCallback(cls, callback:Callable) -> None:
		cls._callback.append(callback)

	@classmethod
	def Log(cls, text:str, tag:str, logType:str) -> None:
		for callback in cls._callback:
			callback('[' + tag + '] ' + text, logType)
