"""
Basic example showing how to read the buttons on I75.
"""

import interstate75

i75 = interstate75.Interstate75(display=interstate75.DISPLAY_INTERSTATE75_128X128)

while True:
    if i75.switch_pressed(interstate75.SWITCH_A):
        print("Switch A pressed")
    if i75.switch_pressed(interstate75.SWITCH_B):
        print("Switch B pressed")
    if i75.switch_pressed(interstate75.SWITCH_BOOT):
        print("Switch Boot pressed")
