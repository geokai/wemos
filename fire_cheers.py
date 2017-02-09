# This script from Tony's Desk, Adafruit Industries tutorials:
# NeoPixels 'Festive Fire' animation.

# This file was created on 29/01/17
# Author: George Kaimakis
# http://github.com/geokai/wemos


###--
#       The Cheerlights feed from thingspeak.com is in the form of a text
#       string on a web page in json format,
#       the entire feed, https://thingspeak.com/channels/1417/feed.json
#       the last 'word' entry, api.thingspeak.com/channels/1417/field/1/last.json
#       the last 'hex' entry, api.thingspeak.com/channels/1417/field/2/last.json
#       Once the pages' contents are obtained, the ujson module can be used to
#       convert the string to a 'dict' object. The relevant value can then be
#       extracted using 'key' indexing.
#       A second thread will be used to make a request to the api at a set interval
#       separate from the main animation 'while' loop and other 'free' running
#       functions.
###--

# modules:
import machine
import neopixel
import uos
import time
#import ujson
#import urequests
#import threading

# global 'setup' variables:
PIXEL_PIN           = 0
PIXEL_WIDTH         = 4
PIXEL_HEIGHT        = 4
FLAME_DIVISOR       = 16.2
RECVD_COLOR         = 'yellow'
PREV_COLOR          = ''
CUR_HUE             = 0
PREV_HUE            = 0

# these variables keep track of elapsed time to control the 'request' loop:
PREVIOUS_MILLIS     = 0
CURRENT_MILLIS      = 0
REQUEST_INTERVAL    = 5
WAIT                = 1000

#host                = 'api.thingspeak.com/'   # Cheerlights API location:
#port                = 80


# look-up dicts:
# colors received from cheerlights API with associated hue values:
flames = {'red':0, 'orange':11, 'yellow':22, 'green':80, 'cyan':110,
'blue':165, 'purple':190, 'magenta':224, 'pink':244}

white = {'white':'val_0'}

warmwhite = {'oldlace':'val_1', 'warmwhite':'val_2'}


###--- definitions ---###

# color space conversion functions - hsl to rgb:
def hue2rgb(p, q, t):
    # Helper for the HSL_to_RGB function:
    # From http://axonflux.com/handy-rgb-to-hsl-and-rgb-to-hsv-color-model-c
    if t < 0:
        t += 1
    if t > 1:
        t -= 1
    if t <1/6:
        return p + (q - p) * 6 * t
    if t < 1/2:
        return q
    if t < 2/3:
        return p + (q - p) * (2/3 - t) * 6
    return p

def HSL_to_RGB(h, s, l):
    # Convert a hue, saturation, lightness color into red, green and blue color.
    # Expects incoming values in range 0...255 and outputs values in same range.
    # From http://axonflux.com/handy-rgb-to-hsl-and-rgb-to-hsv-color-model-c
    h /= 255.0
    s /= 255.0
    l /= 255.0
    r = 0
    g = 0
    b = 0
    if s == 0:
        r = l
        g = l
        b = l
    else:
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue2rgb(p, q, h + 1/3)
        g = hue2rgb(p, q, h)
        b = hue2rgb(p, q, h - 1/3)
    return (int(r*255.0), int(g*255.0), int(b*255.0))


# Create a color palette of flame colors:
def fl_palette(h_offset):
    palette_fl = []
    for x in range(256):
        palette_fl.append(HSL_to_RGB(h_offset + (x // 8), 255, min(255, x * 2)))
        #print(palette_fl[x])
    return palette_fl

# Create a color palette of white colors:
def wh_palette(h_offset):
    palette_wh = []
    for x in range(256):
        palette_wh.append(HSL_to_RGB(h_offset + (x // 8), 255, min(255, x * 2)))
        #print(palette_wh[x])
    return palette_wh

# Create a color palette of warm-white colors:
def wm_palette(h_offset):
    palette_wm = []
    for x in range(256):
        palette_wm.append(HSL_to_RGB(h_offset + (x // 8), 255, min(255, x * 2)))
        #print(palette_wm[x])
    return palette_wm

# transistion smoothly between color sets:
def hue_transistion():
    # transistion from previous to current hue setting:
    pass

# establish connection with API and request payload:
def api_query():
    pass

###---  set-up of objects and initializations  ---###

class FireMatrix:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.data = [0]*(width*height)

    def get(self, x, y):
        x %= self.width     # Wrap around when x value exceeds width bounds:
        y %= self.height    # Like-wise wrap around y value:
        return self.data[y * self.width + x]

    def set(self, x, y, value):
        x %= self.width
        y %= self.height
        self.data[y * self.width + x] = value

# Initiallize neopixels and clear any lit pixels:
np = neopixel.NeoPixel(machine.Pin(PIXEL_PIN), PIXEL_WIDTH * PIXEL_HEIGHT)
np.fill((0,0,0))    # Assumes a 3 component neopixel - rgb only
np.write()

# determine value for CUR_HUE based on color received from broker and call
# palette function:
if RECVD_COLOR in flames:
    CUR_HUE = flames[RECVD_COLOR]
    PALETTE = fl_palette(CUR_HUE)

elif RECVD_COLOR in white:
    CUR_HUE = white[RECVD_COLOR]
    PALETTE = wh_palette(CUR_HUE)

elif RECVD_COLOR in warmwhite:
    CUR_HUE = warmwhite[RECVD_COLOR]
    PALETTE = wm_palette(CUR_HUE)

else:
    #print('Invalid color')
    pass

# Create fire matrix:
fire = FireMatrix(PIXEL_WIDTH, PIXEL_HEIGHT+1)  # Adds an extra line to push
                                                # initial random setting line out
                                                # of view:

# test delay function:
def test_delay(delay):
    time.sleep_ms(delay)


###---  multi-threaded api call  ---###



###---  the main loop  ---###

while True:

###---   the animation loop  ---###
    # set the bottom row to random intensity values (0 to 255):
    for x in range(PIXEL_WIDTH):
        fire.set(x, PIXEL_HEIGHT, int(uos.urandom(1)[0]))
    # Perform a step of flame intensity calculations:
    for x in range(PIXEL_WIDTH):
        for y in range(PIXEL_HEIGHT):
            value = 0
            value += fire.get(x-1, y-1)
            value += fire.get(x, y-1)
            value += fire.get(x+1, y-1)
            value += fire.get(x, y-2)
            value = int(value / FLAME_DIVISOR)
            fire.set(x, y, value)

    # Convert the fire intensity values to neopixel colors and update the pixels:
    for x in range(PIXEL_WIDTH):
        for y in range(PIXEL_HEIGHT):
            np[y * PIXEL_WIDTH + x] = PALETTE[fire.get(x, y)]
    np.write()

    # As these loops run fairly fast, a timing loop is needed to prevent the 
    CURRENT_MILLIS = time.time()
    if CURRENT_MILLIS - PREVIOUS_MILLIS >= REQUEST_INTERVAL:
        test_delay(WAIT)
        PREVIOUS_MILLIS = CURRENT_MILLIS
    # api call being made every time through the while loop.
    # control loop for the api get request:
        # request the contents of the last cheerlights channel feed:
        # extract the color name as a string and asign to a variable:
        # compare current (received) color value with previous:
        # if current value is different, recreate color palette (and run transition):

    time.sleep_ms(50)       # main loop period control:
