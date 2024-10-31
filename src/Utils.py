
class Pointer:
    def __init__(self, value=None):
        self.__value = value

    def SetValue(self, value):
        self.__value = value

    def GetValue(self):
        return self.__value