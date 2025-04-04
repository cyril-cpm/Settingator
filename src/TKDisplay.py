from Display import *
from Setting import *
from tkinter import *
from tkinter import ttk

dict_var = {}

class TKElement(IElement):
    def __init__(self, element, type, variable:Variable, style = None, styleName = "", index = 0):
        IElement.__init__(self)
        self.__type = type
        self.__index = index
        self.__style:ttk.Style = style
        self.__styleName:str = styleName
        self.__element = element
        self.__variable:Variable = variable
        print(f"TKElement créé avec variable: {self.__variable.get()}")

    def SetBGColor(self, color):
        if self.__style and self.__styleName != "":
            self.__style.configure(self.__styleName, background=color)

    def UpdateValue(self, value):
        self.__variable.set(value)

    def GetValue(self):
        return self.__variable.get()
    
    def GetElement(self):
        return self.__element

class TKDisplay(IDisplay):
    def __init__(self) -> None:
        IDisplay.__init__(self)

        self.__root = Tk()

        #self.__root.tk.call('source', 'Forest-ttk-theme-master/forest-dark.tcl')

        self.__style = ttk.Style(self.__root)
        #self.__style.theme_use('forest-dark')

        self.__root.title("Settingator")

        self.__mainFrame = ttk.Frame(self.__root)
        self.__mainFrame.grid(column=0, row=0, sticky=(N, W, E, S))

        #self.__root.columnconfigure(0, weight=1)
        #self.__root.rowconfigure(0, weight=1)

    def Update(self) -> Setting:
        self.UpdateLayout()
        self.__root.update()

    def __UpdateLayout(self, element:LayoutElement, parent, childIndex=0):

        #elementsToRemove = element.GetElementsToRemoveFromView()
        #while elementsToRemove.__len__():
        #    dpg.delete_item(elementsToRemove[0])
        #    element.GetElementsToRemoveFromView().remove(elementsToRemove[0])

        if element.IsNew():
            element.SetNew(False)

            type:int = element.GetType()
            name = element.GetName()
            
            if isinstance(name, Mutable):
                name = name.GetValue()
                
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

            if type == IDP_BUTTON:
                newElement = ttk.Button(parent, text=name, command=lambda e=element : e.Call(None))

            elif type == IDP_TEXT:
                newElement = ttk.Label(parent, textvariable=elementVariable)
                
            elif type == IDP_INPUT:
                newElement = ttk.Entry(parent, textvariable=elementVariable)
                newElement.bind("<Return>", lambda event, e=element : e.Call(elementVariable.get()))
                
                #print("Valeur par défaut:", inputVar.get())

                #if ret:
                #    ret.SetValue(TKElement(newElement, IDP_INPUT))

            elif type == IDP_CHECK:
                newElement = ttk.Checkbutton(parent, text=name, variable=elementVariable, command=lambda e=element : e.Call(elementVariable.get()))
                
                #if element.GetValue() == True:
                #    newElement.state(['selected'])
                #else:
                #    newElement.state(['!selected'])

    

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
 
            newElement.grid(column=column, row=row, sticky=(N, W, E), padx=5, pady=5)
            element.SetIElement(TKElement(newElement, type, elementVariable, self.__style, styleName))
            dict_var[element] = elementVariable
            self.__UpdateChildLayout(element, newElement)

        else:
            self.__UpdateChildLayout(element, element.GetIElement().GetElement())



        element.SetModified(False)

    def __UpdateChildLayout(self, parentElement:LayoutElement, parent) -> None:
        
        if isinstance(parentElement.GetChildren(), list):
            childElement:LayoutElement

            childIndex = 0
            for childElement in parentElement.GetChildren():

                if childElement.IsModified():
                    self.__UpdateLayout(childElement, parent, childIndex)
                
                childIndex += 1

    def UpdateLayout(self) -> None:
        if self._Layout.IsModified():
            self.__UpdateLayout(self._Layout, self.__mainFrame)

    def UpdateSetting(self, setting:Setting) -> None:
        pass

    def IsRunning(self) -> bool:
        return True