# This script from Tony's Desk, Adafruit Industries tutorials:
# NeoPixels 'Festive Fire' animation.

# This file was created on 29/01/17
# Author: George Kaimakis


import machine
import neopixel
import uos
from time import sleep_ms


PIXEL_PIN       = 0
PIXEL_WIDTH     = 4
PIXEL_HEIGHT    = 4
FLAME_DIVISOR   = 16.2
HUE             = 0
RECV_COLOR      = ''

host            = 'http://api.thingspeak.com'
port            = 80



# colors received from cheerlights broker with associated hue values:
flames = {'red':0, 'orange':11, 'yellow':22, 'green':80, 'cyan':110,
'blue':165, 'purple':190, 'magenta':224, 'pink':244}

whites = {'white':'val_0', 'oldlace':'val_1', 'warmwhite':'val_2'}

# determine value for HUE based on color received from broker:
if RECV_COLOR in flames:
    HUE = flames[color]
elif RECV_COLOR in whites:
    HUE = whites[color]
else:
    print('Invalid color')

###--- color space conversion functions - hsl to rgb ---###

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
    # Expects incoming values in range 0...255 and outputs values in ssme range.
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


###---  set-up of objects  ---###

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
np.fill((0,0,0))
np.write()

# Create a color palette of flame colors:
palette_f = []
for x in range(256):
    palette_f.append(HSL_to_RGB(HUE + (x // 8), 255, min(255, x * 2)))
    print(palette_f[x])

# Create a color palette of white colors:
#palette_w = []
#for x in range(256):
#    palette_w.append(HSL_to_RGB(HUE + (x // 8), 255, max(128, x * 2)))
#    print(palette_w[x])

# Create fire matrix:
fire = FireMatrix(PIXEL_WIDTH, PIXEL_HEIGHT+1)


###---  the animation  ---###

while True:
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
            #fire.set(x, y, value)

    # Convert the fire intensity values to neopixel colors and update the pixels:
    for x in range(PIXEL_WIDTH):
        for y in range(PIXEL_HEIGHT):
            np[y * PIXEL_WIDTH + x] = palette_f[fire.get(x, y)]
    np.write()
    sleep_ms(50)
