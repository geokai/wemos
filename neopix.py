from neopixel import *
from machine import Pin
import time
import sys

#print(sys.argv[0])
#print(sys.arg[1])
#print(sys.arg[2])

red     = 128
green   = 0
blue    = 128

pin = Pin(0, Pin.OUT)
#pin.high()
np = NeoPixel(pin, 1)

np[0] = (red, green, blue)
np.write()
