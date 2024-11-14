from Display import *
from Setting import *
import dearpygui.dearpygui as dpg

dpg.create_context()
dpg.configure_app(manual_callback_management=True)

<<<<<<< HEAD
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
            dpg.highlight_table_cell(self._value+"table", 0, self.__index, hexColorToList(color))
            
            #pos = dpg.get_item_pos(self._value)
            #size = dpg.get_item_rect_size(self._value)
            #cornerPos = [pos[0] + size[0], pos[1] + size[1]]
            #dpg.draw_rectangle(pos, cornerPos, fill=hexColorToList(color), parent="VPDrawList")

    def UpdateValue(self, value):
        dpg.set_value(self._value, value)

=======
>>>>>>> 8cbc806 (Start implementing DearPyGUI)
class DearPyGUIDisplay(IDisplay):
    def __init__(self) -> None:
        IDisplay.__init__(self)

<<<<<<< HEAD
        dpg.create_viewport(title="Settingator", width=1200, height=1200)
        dpg.setup_dearpygui()
        #dpg.toggle_viewport_fullscreen()
        dpg.show_viewport()

        self.__mainWindow = dpg.add_window(tag="Main Window", width=600, height=600, no_background=False, no_title_bar=True, pos=[0, 0])
        self.__mainGroup = dpg.add_group(tag="Main Group", parent=self.__mainWindow)
        #dpg.add_viewport_drawlist(tag="VPDrawList", front=False)
=======
        dpg.create_viewport(title="Settingator")
        dpg.setup_dearpygui()
        dpg.show_viewport()

        with dpg.window(tag="Main Window") as mainWindow:
                        pass

        self.__mainWindow = mainWindow
>>>>>>> 8cbc806 (Start implementing DearPyGUI)

        dpg.set_primary_window("Main Window", True)

    def Update(self) -> Setting:
        jobs = dpg.get_callback_queue() # retrieves and clears queue
        dpg.run_callbacks(jobs)

        self.UpdateLayout(None)
        dpg.render_dearpygui_frame()

<<<<<<< HEAD
    def __UpdateChildLayout(self, parentElement:LayoutElement, columnTag = None) -> None:
        
        if isinstance(parentElement.GetKey(), list):
            childElement:LayoutElement

            childIndex = 0
            for childElement in parentElement.GetKey():

                if childElement.IsModified():
                    self.__UpdateLayout(childElement, columnTag, childIndex)
                
                childIndex += 1

    def __UpdateLayout(self, element:LayoutElement, columnTag=None, childIndex=0):

        elementsToRemove = element.GetElementsToRemoveFromView()
        while elementsToRemove.__len__():
            dpg.delete_item(elementsToRemove[0])
            element.GetElementsToRemoveFromView().remove(elementsToRemove[0])
=======
    def __UpdateChildLayout(self, parentElement:PreLayoutElement, columnTag = None) -> None:
        
        if isinstance(parentElement.GetKey(), list):
            childElement:PreLayoutElement

            for childElement in parentElement.GetKey():

                if childElement.IsModified():
                    self.__UpdatePrelayout(childElement, columnTag)

    def __UpdatePrelayout(self, element:PreLayoutElement, columnTag=None):

        for elementToRemove in element.GetElementsToRemoveFromView():
            print("item to delete")
            dpg.delete_item(elementToRemove)
            element.GetElementsToRemoveFromView().remove(elementToRemove)
>>>>>>> 8cbc806 (Start implementing DearPyGUI)

        if element.IsNew():
            element.SetNew(False)

            type:int = element.GetType()
            name = element.GetName()
<<<<<<< HEAD
=======
            
            if isinstance(name, Pointer):
                name = name.GetValue()

            key = element.GetKey()
            ret:Pointer = element.GetRet()
>>>>>>> 8cbc806 (Start implementing DearPyGUI)

            parentTag = parent=str(element.GetParent()) if element.GetParent() else columnTag
                
            if type == IDP_BUTTON:
                dpg.add_button(label=name, tag=str(element), parent=columnTag, callback=key)
<<<<<<< HEAD
                

            elif type == IDP_TEXT:
                dpg.add_text(default_value=name, tag=str(element), parent=columnTag)
                

            elif type == IDP_INPUT:
                dpg.add_input_text(default_value=name, tag=str(element), parent=columnTag, width=200)


            elif type == IDP_COLUMN:
                dpg.add_group(tag=str(element)+"columnBody", parent=columnTag, label=name, horizontal=False)
                
                #dpg.add_table(tag=str(element)+"table", parent=columnTag, header_row=False, policy=dpg.mvTable_SizingFixedFit)
                #dpg.add_table_column(tag=str(element)+"column", parent=str(element)+"table")
                #dpg.add_table_row(tag=str(element)+"row", parent=str(element)+"table")
                #dpg.add_table_cell(tag=str(element)+"cell", parent=str(element)+"row")
                #dpg.highlight_table_cell(str(element)+"table", 0, 0, hexColorToList("#00FF00"))
                #dpg.add_group(tag=str(element)+"columnBody", parent=str(element)+"cell")

                if ret:
                    ret.SetValue(DPGElement(str(element), IDP_COLUMN))

                self.__UpdateChildLayout(element, str(element)+"columnBody")

            elif type == IDP_FRAME:
                #dpg.add_group(tag=str(element), parent=columnTag, label=name)
                
                #dpg.add_group(tag=str(element)+"preGroup", parent=columnTag, horizontal=False)

                dpg.add_table(tag=str(element)+"table", parent=columnTag, header_row=False, policy=dpg.mvTable_SizingFixedFit)
                dpg.add_table_column(tag=str(element)+"column", parent=str(element)+"table")
                dpg.add_table_row(tag=str(element)+"row", parent=str(element)+"table")
                dpg.add_table_cell(tag=str(element)+"cell", parent=str(element)+"row")
                #dpg.add_group(tag=str(element)+"cellGroup", parent=str(element)+"cell")

                if name != '':
                    dpg.add_text(tag=str(element) + "label", parent=str(element)+"cell", default_value=name)
                    
                    dpg.highlight_table_cell(str(element)+"table", 0, 0, hexColorToList("#0000FF"))

                #dpg.add_group(tag=str(element)+"frameBody", parent=str(element)+"cell", horizontal=True)

                if ret:
                    ret.SetValue(DPGElement(str(element), IDP_FRAME, 0))

                self.__UpdateChildLayout(element, str(element)+"cell")
=======

            elif type == IDP_TEXT:
                dpg.add_text(default_value=name, tag=str(element), parent=columnTag)

            elif type == IDP_INPUT:
                dpg.add_input_text(default_value=name, tag=str(element), parent=columnTag)

            elif type == IDP_COLUMN:
                dpg.add_table_cell(tag=str(element), parent=columnTag)
                #self.__UpdateChildLayout(element, str(element))
            
            elif type == IDP_FRAME:
                if columnTag == self.__mainWindow:
                    dpg.add_table(tag=str(element), parent=columnTag, header_row=False)

                    for x in range(0, key.__len__()):
                        dpg.add_table_column(tag=str(element)+str(x), parent=str(element))
                    
                    dpg.add_table_row(tag=str(element)+"row", parent=str(element))

                else:
                    dpg.add_table_cell(tag=str(element), parent=columnTag)

                    if name != '':
                        dpg.add_text(default_value=name, tag=str(element)+"label", parent=str(element))

                    dpg.add_table(tag=str(element)+"table", parent=str(element), header_row=False)


                    for x in range(0, key.__len__()):
                        dpg.add_table_column(tag=str(element)+str(x), parent=str(element)+"table")

                    dpg.add_table_row(tag=str(element)+"row", parent=str(element)+"table")

                #self.__UpdateChildLayout(element, str(element)+"row")
        
        if element.GetType() == IDP_FRAME:
            self.__UpdateChildLayout(element, str(element)+"row")

        elif element.GetType() == IDP_COLUMN:
            self.__UpdateChildLayout(element, str(element))
>>>>>>> 8cbc806 (Start implementing DearPyGUI)

        element.SetModified(False)

                    

    def UpdateLayout(self, slaveSettings:dict) -> None:
<<<<<<< HEAD
        if self._Layout.IsModified():
            self.__UpdateLayout(self._Layout, self.__mainGroup)

        if slaveSettings:
            pass


=======
        if self._PreLayout.IsModified():
            self.__UpdatePrelayout(self._PreLayout, self.__mainWindow)
>>>>>>> 8cbc806 (Start implementing DearPyGUI)

    def UpdateSetting(self, setting:Setting) -> None:
        pass
        
    def IsRunning(self) -> bool:
        return dpg.is_dearpygui_running()