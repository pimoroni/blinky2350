"""
Vector font demo! Vector fonts are slower but smoother. They are best used for large text.

You will need to copy the .af font file to your I75.
(this script assumes it is in the /basic directory).

Find out how to convert your own fonts to .af here: https://github.com/lowfatcode/alright-fonts
"""

from interstate75 import Interstate75, DISPLAY_INTERSTATE75_128X128
from picovector import ANTIALIAS_BEST, PicoVector, Transform

i75 = Interstate75(display=DISPLAY_INTERSTATE75_128X128)
display = i75.display

WIDTH = i75.width
HEIGHT = i75.height

# Couple of colours for use later
PINK = display.create_pen(250, 125, 180)
BLACK = display.create_pen(0, 0, 0)

# Pico Vector
vector = PicoVector(display)
vector.set_antialiasing(ANTIALIAS_BEST)

t = Transform()
vector.set_transform(t)

# Set our font, size and spacing.
# Don't forget to transfer the font file to the I75W
vector.set_font("/basic/cherry-hq.af", 55)
vector.set_font_letter_spacing(100)
vector.set_font_word_spacing(100)


while True:
    # Clear the display
    display.set_pen(BLACK)
    display.clear()

    # Set the pen colour for our text
    display.set_pen(PINK)

    # Draw our text!
    vector.text("Hello!", 10, 75)

    # Update the display
    i75.update()
