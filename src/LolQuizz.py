from PySerialCommunicator import GetPortList, SerialCTR
from Settingator import *
from TKDisplay import *
from pygame import display, mixer as mx

if __name__ == "__main__":

	portList = GetPortList()



	#sound init
	mx.init(channels=1)

	display = TKDisplay()

	STR = Settingator(display)

	while display.IsRunning():
		STR.Update()
