"""
This example lets you display an animated "gif" (we're actually cycling quickly through a series of PNG images).

First resize your gif to 128x128 pixels (we used https://ezgif.com/resize for this).

Then use https://ezgif.com/split (and 'Output images in PNG format') to split the gif into individual frames.

Save the individual frames in a folder on your I75 called "gif" (or change the folder name in the code below).

Check out https://1jps.tumblr.com/ for many nice retro video game gifs!

"""

import time
from interstate75 import Interstate75, DISPLAY_INTERSTATE75_128X128
import pngdec
import os

# Time to pause between frames
INTERVAL = 0.04

# The name of the folder that the files are stored in
DIR = "gif"

# Setup for the display
i75 = Interstate75(display=DISPLAY_INTERSTATE75_128X128)
display = i75.display

p = pngdec.PNG(display)


while True:

    # make a list of files in the gif folder
    files = os.listdir(DIR)

    # open each file in the gif folder
    for file in files:
        if file.endswith(".png" or ".PNG"):
            img = DIR + "/" + file

        p.open_file(img)

        # Decode our PNG file and set the X and Y
        p.decode(0, 0)

        i75.update()
        print("Displaying: " + img)

        time.sleep(INTERVAL)
