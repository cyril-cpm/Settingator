from Display import *
from Setting import *
from tkinter import *
from tkinter import ttk

class TKElement(IElement):
    def __init__(self, value, type, index = 0):
        IElement.__init__(self, value)
        self.__type = type
        self.__index = index

    def SetBGColor(self, color):
        print("Change BG Color")

    def UpdateValue(self, value):
        print("Update Value")

class TKDisplay(IDisplay):
    def __init__(self) -> None:
        IDisplay.__init__(self)

        self.__root = Tk()

        self.__root.title("Settingator")

        self.__mainFrame = ttk.Frame(self.__root)
        self.__mainFrame.grid(column=0, row=0, sticky=(N, W, E, S))
        
        #self.__root.columnconfigure(0, weight=1)
        #self.__root.rowconfigure(0, weight=1)

        #testBUtton = ttk.Button(self.__mainFrame, text="Test", command=lambda : print("yolo")).grid(column=0, row=0)

    def Update(self) -> Setting:
        self.__root.update()
        self.UpdateLayout(None)

    def __UpdatePrelayout(self, element:PreLayoutElement, parent, childIndex=0):

        #elementsToRemove = element.GetElementsToRemoveFromView()
        #while elementsToRemove.__len__():
        #    dpg.delete_item(elementsToRemove[0])
        #    element.GetElementsToRemoveFromView().remove(elementsToRemove[0])

        if element.IsNew():
            element.SetNew(False)

            type:int = element.GetType()
            name = element.GetName()
            
            if isinstance(name, Pointer):
                name = name.GetValue()

            key = element.GetKey()
            ret:Pointer = element.GetRet()
                
            row = 1
            column = 1

            newElement:ttk.Widget

            if element.GetParent():
                if element.GetParent().GetType() == IDP_FRAME:
                    column = childIndex + 1

                elif element.GetParent().GetType() == IDP_COLUMN:
                    row = childIndex + 1

            if type == IDP_BUTTON:
                newElement = ttk.Button(parent, text=name, command=key)
                
                if ret:
                    ret.SetValue(TKElement(newElement, IDP_BUTTON))

            elif type == IDP_TEXT:
                
                newElement = ttk.Label(parent, text=name)
                
                if ret:
                    ret.SetValue(TKElement(newElement, IDP_TEXT))

            elif type == IDP_INPUT:
                inputVar=StringVar(value=name)
                newElement = ttk.Entry(parent, textvariable=inputVar)

                if ret:
                    ret.SetValue(TKElement(newElement, IDP_INPUT))

            elif type == IDP_COLUMN:
                newElement = ttk.Frame(parent)

                if ret:
                    ret.SetValue(TKElement(newElement, IDP_COLUMN))


            elif type == IDP_FRAME:

                if name == '':
                    newElement = ttk.Frame(parent)
                else:
                    newElement = ttk.LabelFrame(parent, text=name)

                if ret:
                    ret.SetValue(TKElement(newElement, IDP_FRAME))
 
            newElement.grid(column=column, row=row, sticky=(N,S,E,W), padx=5, pady=5)

            self.__UpdateChildLayout(element, newElement)


        element.SetModified(False)

    def __UpdateChildLayout(self, parentElement:PreLayoutElement, parent) -> None:
        
        if isinstance(parentElement.GetKey(), list):
            childElement:PreLayoutElement

            childIndex = 0
            for childElement in parentElement.GetKey():

                if childElement.IsModified():
                    self.__UpdatePrelayout(childElement, parent, childIndex)
                
                childIndex += 1

    def UpdateLayout(self, slaveSettings:dict) -> None:
        if self._PreLayout.IsModified():
            self.__UpdatePrelayout(self._PreLayout, self.__mainFrame)

        if slaveSettings:
            pass

    def UpdateSetting(self, setting:Setting) -> None:
        pass

    def IsRunning(self) -> bool:
        return True