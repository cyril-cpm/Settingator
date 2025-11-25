from Display import *
from Setting import *
from tkinter import *
from tkinter import ttk
import queue
from weakref import WeakMethod
import sys
import gc

dict_var = {}

class TKElement(IElement):
	def __init__(self, display, element, type, variable:Variable, style = None, styleName = "", index = 0):
		IElement.__init__(self)
		self.__type = type
		self.__index = index
		self.__style:ttk.Style = style
		self.__styleName:str = styleName
		self.__element:ttk.Widget = element
		self.__variable:Variable = variable
		self.__display:TKDisplay = display
		print(f"TKElement créé avec variable: {self.__variable.get()}")

 #	 def __del__(self):
 #		 self.__element.destroy()

	def SetBGColor(self, color):
		if self.__style and self.__styleName != "":
			self.__display.PutUpdateBGColor(self, color)

	def UpdateBGColor(self, color):
			self.__style.configure(self.__styleName, background=color)

	def UpdateValue(self, value):
		self.__display.PutUpdateValue(self, value)

	def GetValue(self):
		return self.__variable.get()
	
	def GetElement(self):
		return self.__element
	
	def GetVariable(self) -> Variable:
		return self.__variable
	
	def SetEnable(self, value):
		if (value == '' or value == '0'):
			value = False
		else:
			value = True

		if value:
			self.__display.PutFunction(self.__element.state, (['!disabled'],))
		else:
			self.__display.PutFunction(self.__element.state, (['disabled'],))

	def SetVisible(self, value):
		if (value == '' or value == '0' or value == False):
			value = False
		else:
			value = True

		if value:
			self.__display.PutFunction(self.__element.grid, ())
		else:
			self.__display.PutFunction(self.__element.grid_remove,())


class TKDisplay(IDisplay):
	def __init__(self) -> None:
		IDisplay.__init__(self)

		self.__root = Tk()
		self.__root.update()

		#self.__root.tk.call('source', 'Forest-ttk-theme-master/forest-dark.tcl')

		self.__style = ttk.Style(self.__root)
		#self.__style.theme_use('forest-dark')

		self.__root.title("Settingator")

		self.__mainFrame = ttk.Frame(self.__root)
		self.__mainFrame.grid(column=0, row=0, sticky=(N, W, E, S))

		#self.__root.columnconfigure(0, weight=1)
		#self.__root.rowconfigure(0, weight=1)

		self.__updateValuesQueue = queue.Queue()
		self.__updateBGColorQueue = queue.Queue()

		self.__functionQueue = queue.Queue()

		def on_close():
			print("La fenêtre a été fermée")
			self.__root.destroy()
			self._isRunning = False

		self.__root.protocol("WM_DELETE_WINDOW", on_close)

	def Update(self) -> None:
		self.UpdateLayout()
		self.UpdateValues()
		self.UpdateBGColors()
		self.ExecuteFunctionQueue()
		self.__root.update()

	def PutUpdateBGColor(self, element:TKElement, color):
		self.__updateBGColorQueue.put((element, color))

	def PutUpdateValue(self, element:TKElement, value):
		self.__updateValuesQueue.put((element, value))

	def PutFunction(self, function:callable, args:tuple) -> None:
		self.__functionQueue.put((function, args))

	def ExecuteFunctionQueue(self) -> None:
		while True:
			try:
				f, args = self.__functionQueue.get_nowait()
				f(*args)

			except queue.Empty:
				break

	def UpdateValues(self) -> None:
		while True:
			try:
				element, value = self.__updateValuesQueue.get_nowait()
				element.GetVariable().set(value)
			except queue.Empty:
				break

	def UpdateBGColors(self):
		while True:
			try:
				element, color = self.__updateBGColorQueue.get_nowait()
				element.UpdateBGColor(color)
			except queue.Empty:
				break

	def __UpdateLayout(self, element:LayoutElement, parent, childIndex=0):

		#elementsToRemove = element.GetElementsToRemoveFromView()
		#while elementsToRemove.__len__():
		#	 dpg.delete_item(elementsToRemove[0])
		#	 element.GetElementsToRemoveFromView().remove(elementsToRemove[0])

		if element.IsNew():
			element.SetNew(False)

			type:int = element.GetType()

			if type != IDP_WRAPPER:
				name = element.GetName()
				
				row = 1
				column = 1

				newElement:ttk.Widget

				styleName = str(element)

				elementVariable = StringVar(master=self.__root, value=element.GetValue())

				if element.GetParent():
					if element.GetParent().GetType() == IDP_FRAME:
						column = childIndex + 1

					elif element.GetParent().GetType() == IDP_COLUMN:
						row = childIndex + 1
					
					elif element.GetParent().GetType() == IDP_WRAPPER:
						if element.GetParent().GetParent():
							if element.GetParent().GetParent().GetType() == IDP_FRAME:
								column = childIndex + 1

							elif element.GetParent().GetParent().GetType() == IDP_COLUMN:
								row = childIndex + 1

				weakMethod = WeakMethod(element.Call)

				if type == IDP_BUTTON:
					newElement = ttk.Button(parent, text=name, command=lambda w=weakMethod: w() and w()(None))

				elif type == IDP_TEXT:
					styleName += ".TLabel"
					self.__style.configure(styleName)
					newElement = ttk.Label(parent, textvariable=elementVariable, style=styleName)
				
				elif type == IDP_INPUT:
					newElement = ttk.Entry(parent, textvariable=elementVariable)
					newElement.bind("<Return>", lambda event, w=weakMethod: w() and w()(elementVariable.get()))
				
				elif type == IDP_CHECK:
					newElement = ttk.Checkbutton(parent, text=name, variable=elementVariable, command=lambda w=weakMethod: w() and w()(elementVariable.get()))
				 
				elif type == IDP_COLUMN:
				
					if name == "":
						styleName += ".TFrame"
						self.__style.configure(styleName)
						newElement = ttk.Frame(parent, style=styleName)
					else:
						styleName += ".TLabelframe"
						self.__style.configure(styleName)
						newElement = ttk.Labelframe(parent, text=name, style=styleName)

				elif type == IDP_FRAME:

					if name == '':
						newElement = ttk.Frame(parent)
					else:
						styleName += ".TLabelframe"
						self.__style.configure(styleName)
						newElement = ttk.Labelframe(parent, text=name, style=styleName)
 
				newElement.grid(column=column, row=row, sticky=element.GetStick(), padx=5, pady=5)
				element.SetIElement(TKElement(self, newElement, type, elementVariable, self.__style, styleName))
				self.__UpdateChildLayout(element, newElement)

			else:
				self.__UpdateChildLayout(element, element.GetParent().GetIElement().GetElement(), wrapperIndex=childIndex)


		elif (element and element.GetIElement()):
			if element.GetType() == IDP_WRAPPER:
				self.__UpdateChildLayout(element, element.GetParent().GetIElement().GetElement(), wrapperIndex=childIndex)
			else:
				self.__UpdateChildLayout(element, element.GetIElement().GetElement())



		element.SetModified(False)

	def __UpdateChildLayout(self, parentElement:LayoutElement, parent, wrapperIndex=0) -> None:
		
		if isinstance(parentElement.GetChildren(), list):
			childElement:LayoutElement

			childIndex = 0
			for childElement in parentElement.GetChildren():

				if childElement and childElement.IsModified():
					self.__UpdateLayout(childElement, parent, childIndex + wrapperIndex)
				
				childIndex += 1

	def UpdateLayout(self) -> None:
		if self._Layout.IsModified():
			self.__UpdateLayout(self._Layout, self.__mainFrame)


	def IsRunning(self) -> bool:
		return self._isRunning
