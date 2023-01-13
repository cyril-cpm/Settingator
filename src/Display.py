from abc import ABC, abstractmethod
from typing import Type
from Setting import *

class IDisplay(ABC):
    @abstractmethod
    def __init__(self,)