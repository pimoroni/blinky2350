"""
Basic example showing how to light up the RGB LED on the I75 board.
"""

from interstate75 import Interstate75
from time import sleep

i75 = Interstate75(display=Interstate75.DISPLAY_INTERSTATE75_128X128)

# Cycle through RGB

while True:
    i75.set_led(255, 0, 0)
    sleep(1)
    i75.set_led(0, 255, 0)
    sleep(1)
    i75.set_led(0, 0, 255)
    sleep(1)
