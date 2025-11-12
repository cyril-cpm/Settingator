from abc import ABC, abstractmethod
from typing import Type
from Utils import *
import weakref

#enum display
IDP_NONE = 0x00
IDP_BUTTON = 0x01
IDP_INPUT = 0x02
IDP_TEXT = 0x03
IDP_FRAME = 0x04
IDP_COLUMN = 0x05
IDP_CHECK = 0x06
IDP_SLIDER = 0x07
IDP_WRAPPER = 0x08

def IDPTypeToStr(IDPType:int = IDP_NONE):
	if IDPType == IDP_NONE:
		return "IDP_NONE"
	elif IDPType == IDP_BUTTON:
		return "IDP_BUTTON"
	elif IDPType == IDP_INPUT:
		return "IDP_INPUT"
	elif IDPType == IDP_TEXT:
		return "IDP_TEXT"
	elif IDPType == IDP_FRAME:
		return "IDP_FRAME"
	elif IDPType == IDP_COLUMN:
		return "IDP_COLUMN"
	elif IDPType == IDP_WRAPPER:
		return "IDP_WRAPPER"
	else:
		return "IDP_UNKNOWN"
		

class IElement(ABC):
	def __init__(self):
		pass

	def __del__(self):
		pass

	@abstractmethod
	def SetBGColor(self, color):
		pass

	@abstractmethod
	def UpdateValue(self, value):
		pass

	@abstractmethod
	def GetValue(self):
		pass

	@abstractmethod
	def GetElement(self):
		pass

	@abstractmethod
	def SetEnable(self, value:bool):
		pass

	@abstractmethod
	def SetVisible(self, value):
		pass


class LayoutElement(ABC):
	def __init__(self, type, value=None, name="", children:list|None=None, callback=None, stick="nsew") -> None:
		self._type = type
		self._name = name
		self.__value = value
		self._parent:LayoutElement|None = None
		self._isModified:bool = True
		self._isNew:bool = True
		self.__callback = callback
		self.__stick = stick

		self.__iElement:IElement|None = None

		self._children:list|None = children

		if isinstance(self._children, list):
			for element in self._children:
				if element:
					element.SetParentRecursively(self)

		if (type == IDP_COLUMN or type == IDP_FRAME) and children == None:
			self._children = []

	def __del__(self):
		pass

	def GetStick(self) -> str:
		return self.__stick

	def IsNew(self):
		return self._isNew
	
	def SetNew(self, value:bool):
		self._isNew = value

	def GetElementsToRemoveFromView(self):
		return self.__toRemoveFromView
	
	def GetElementsToAddInView(self):
		return self.__toAddInView

	def GetType(self):
		return self._type
	
	def GetName(self):
		return self._name
	
	def GetValue(self):
		return self.__value
	
	def SetValue(self, value):
		self.__value = value

	def UpdateValue(self, value):
		self.SetValue(value)
		
		if not self.IsNew():
			if self.__iElement != None:
				self.__iElement.UpdateValue(value)
	
	def GetChildren(self):
		return self._children
	
	def GetIElement(self) -> IElement|None:
		return self.__iElement
	
	def SetIElement(self, element:IElement) -> None:
		self.__iElement = element

	def SetParent(self, parent = None) -> None:
		if parent == None:
			self._parent = None
		else:
			self._parent = weakref.ref(parent)

	def SetParentRecursively(self, parent = None) -> None:
		if parent != None:
			self._parent = weakref.ref(parent)
		else:
			self._parent = None

		if isinstance(self._children, list):
			for element in self._children:
				element.SetParentRecursively(self)
	
	def GetParent(self, n = 1):
		if n > 1:
			return self.GetParent(n-1)

		if self._parent:
			return self._parent()
		return self._parent
	
	def SetModified(self, modified:bool = True):
		self._isModified = modified

		if modified and self._parent and self._parent():
			self._parent().SetModified()

	def IsModified(self) -> bool:
		return self._isModified
	
	def AppendElements(self, elements:list) -> None:
		if isinstance(self._children, list):
			for element in elements:
				self._children.append(element)
				element.SetParent(self)

			#self.__toAddInView.append(element)
			self.SetModified()
			
		else:
			print("Can't append element to " + IDPTypeToStr(self._type) + ", name is \"" + self._name + "\"")
			print("children:")
			print(str(self._children))

	def AppendElement(self, element) -> None:
		if isinstance(self._children, list):
			self._children.append(element)
			element.SetParent(self)

			#self.__toAddInView.append(element)
			self.SetModified()
			
		else:
			print("Can't append element to " + IDPTypeToStr(self._type) + ", name is \"" + self._name + "\"")
			print("children:")
			print(str(self._children))

	def RemoveElement(self, element) -> None:
		if isinstance(self._children, list):

			if element in self._children:
				self.SetModified()
				element.SetParent()
				self._children.remove(element)
				
				#self.__toRemoveFromView.append(str(element))
		else:
			print("Can't remove element to " + IDPTypeToStr(self._type) + ", name is \"" + self._name + "\"")
			print("children:")
			print(str(self._children))

	def Call(self, value = None):
		if self.__callback != None:
			self.__callback(value)

	def SetEnable(self, value):
		self.__iElement.SetEnable(value)

		if isinstance(self._children, list):
			for children in self._children:
				children.SetEnable(value)

	def SetVisible(self, value):
		self.__iElement.SetVisible(value)

class IDisplay(ABC):
	def __init__(self) -> None:
		self.__slaveSettings = dict
		self._Layout = LayoutElement(IDP_COLUMN)
		self._isRunning = True

	def SetSlaveSettingsRef(self, slaveSettings:dict) -> None:
		self.__slaveSettings = slaveSettings

	def GetSlaveSettings(self) -> dict:
		return self.__slaveSettings

	@abstractmethod
	def Update(self) -> None:
		pass

	@abstractmethod
	def UpdateLayout(self) -> None:
		pass

	@abstractmethod
	def IsRunning(self) -> bool:
		pass

	def AddLayout(self, element:LayoutElement) -> None:
		self._Layout.AppendElement(element)

	def RemoveLayout(self, element:LayoutElement) -> None:
		self._Layout.RemoveElement(element)

	def GetLayout(self) -> list:
		return self._Layout
