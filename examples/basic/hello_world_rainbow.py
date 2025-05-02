"""
Fancy bitmap font demo!
"""

from interstate75 import Interstate75
import time

i75 = Interstate75(display=Interstate75.DISPLAY_INTERSTATE75_128X128)
graphics = i75.display

WIDTH, HEIGHT = graphics.get_bounds()

# variable to keep track of pen hue
hue = 0.0

graphics.set_font("bitmap8")

for i in range(54):
    # create a pen and set the drawing color
    PEN_COLOUR = graphics.create_pen_hsv(hue, 1.0, 0.75)
    graphics.set_pen(PEN_COLOUR)
    # draw text
    graphics.text("Hello i75", 4, i * 2, scale=3)
    # increment hue
    hue += 1.0 / 54
    i75.update()
    time.sleep(0.03)

while True:
    # create a pen and set the drawing color
    PEN_COLOUR = graphics.create_pen_hsv(hue, 1.0, 1.0)
    graphics.set_pen(PEN_COLOUR)
    # draw text
    graphics.text("Hello i75", 4, i * 2, scale=3)
    # increment hue
    hue += 1.0 / 54
    i75.update()
    time.sleep(0.05)
