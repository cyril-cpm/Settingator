from Display import *
from Setting import *
import dearpygui.dearpygui as dpg

dpg.create_context()
dpg.configure_app(manual_callback_management=True)

def hexColorToList(color:str) -> list:
    r = color [1:3]
    g = color [3:5]
    b = color [5:7]

    ret = [int(r, 16), int(g, 16), int(b, 16)]

    return ret

class DPGElement(IElement):
    def __init__(self, value, type, index = 0):
        IElement.__init__(self, value)
        self.__type = type
        self.__index = index

    def SetBGColor(self, color):
        
        if self.__type == IDP_FRAME:
            #dpg.highlight_table_cell(self._value, 0, self.__index, hexColorToList(color))
            pos = dpg.get_item_pos(self._value)
            size = dpg.get_item_rect_size(self._value)
            cornerPos = [pos[0] + size[0], pos[1] + size[1]]
            dpg.draw_rectangle(pos, cornerPos, fill=hexColorToList(color), parent="Main Window")

    def UpdateValue(self, value):
        dpg.set_value(self._value, value)

class DearPyGUIDisplay(IDisplay):
    def __init__(self) -> None:
        IDisplay.__init__(self)

        dpg.create_viewport(title="Settingator")
        dpg.setup_dearpygui()
        dpg.show_viewport()

        with dpg.window(tag="Main Window") as mainWindow:
                        pass

        self.__mainWindow = mainWindow

        dpg.set_primary_window("Main Window", True)

    def Update(self) -> Setting:
        jobs = dpg.get_callback_queue() # retrieves and clears queue
        dpg.run_callbacks(jobs)

        self.UpdateLayout(None)
        dpg.render_dearpygui_frame()

    def __UpdateChildLayout(self, parentElement:PreLayoutElement, columnTag = None) -> None:
        
        if isinstance(parentElement.GetKey(), list):
            childElement:PreLayoutElement

            childIndex = 0
            for childElement in parentElement.GetKey():

                if childElement.IsModified():
                    self.__UpdatePrelayout(childElement, columnTag, childIndex)
                
                childIndex += 1

    def __UpdatePrelayout(self, element:PreLayoutElement, columnTag=None, childIndex=0):

        elementsToRemove = element.GetElementsToRemoveFromView()
        while elementsToRemove.__len__():
            dpg.delete_item(elementsToRemove[0])
            element.GetElementsToRemoveFromView().remove(elementsToRemove[0])

        if element.IsNew():
            element.SetNew(False)

            type:int = element.GetType()
            name = element.GetName()
            
            if isinstance(name, Pointer):
                name = name.GetValue()

            key = element.GetKey()
            ret:Pointer = element.GetRet()

            parentTag = parent=str(element.GetParent()) if element.GetParent() else columnTag
                
            if type == IDP_BUTTON:
                dpg.add_button(label=name, tag=str(element), parent=columnTag, callback=key)
                
                if ret:
                    ret.SetValue(DPGElement(str(element), IDP_BUTTON))

            elif type == IDP_TEXT:
                dpg.add_text(default_value=name, tag=str(element), parent=columnTag)
                
                if ret:
                    ret.SetValue(DPGElement(str(element), IDP_TEXT))

            elif type == IDP_INPUT:
                dpg.add_input_text(default_value=name, tag=str(element), parent=columnTag, width=200)

                if ret:
                    ret.SetValue(DPGElement(str(element), IDP_INPUT))

            elif type == IDP_COLUMN:
                dpg.add_group(tag=str(element), parent=columnTag)

                if ret:
                    ret.SetValue(DPGElement(str(element), IDP_COLUMN))
            
            elif type == IDP_FRAME:
                dpg.add_group(tag=str(element), parent=columnTag, label=name)
                
                if name != '':
                    dpg.add_text(tag=str(element) + "label", parent=str(element), default_value=name)

                dpg.add_group(tag=str(element)+"frameBody", parent=str(element), horizontal=True)

                if ret:
                    ret.SetValue(DPGElement(str(element), IDP_FRAME, childIndex))

                #self.__UpdateChildLayout(element, str(element)+"row")

        if element.GetType() == IDP_FRAME:
            self.__UpdateChildLayout(element, str(element)+"frameBody")

        elif element.GetType() == IDP_COLUMN:
            self.__UpdateChildLayout(element, str(element))

        element.SetModified(False)

                    

    def UpdateLayout(self, slaveSettings:dict) -> None:
        if self._PreLayout.IsModified():
            self.__UpdatePrelayout(self._PreLayout, self.__mainWindow)


    def UpdateSetting(self, setting:Setting) -> None:
        pass
        
    def IsRunning(self) -> bool:
        return dpg.is_dearpygui_running()