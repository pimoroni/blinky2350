"""
This example displays multiple animated "gifs" (we're actually cycling quickly through a series of PNG images)

First resize your gif to 128x128 pixels (we used https://ezgif.com/resize).

Then use https://ezgif.com/split (and 'Output images in PNG format') to split the gif into individual frames.

Save each GIF into a seperate folder on your Pico.

Check out https://1jps.tumblr.com/ for many nice retro video game gifs!

"""

import time
from interstate75 import Interstate75, DISPLAY_INTERSTATE75_128X128
import pngdec
import os
import random

# Time to pause between frames (in seconds)
FRAME_INTERVAL = 0.04

# How long to display each GIF for (in seconds)
GIF_INTERVAL = 2

# Setup for the display
i75 = Interstate75(display=DISPLAY_INTERSTATE75_128X128)
display = i75.display

p = pngdec.PNG(display)


def new_directory():
    global files, dir
    # add directories to the list
    dirs = []
    for f in os.ilistdir():
        if f[1] == 0x4000:
            dirs.append(f[0])
    # switch to a new directory and list the .png and .PNG files that are in it
    dir = random.choice(dirs)
    print(f"Switching to {dir}!")
    files = os.listdir(dir)
    # if no images are found, call the function again
    if not any(file.endswith(".png" or ".PNG") for file in files):
        new_directory()


# start a timer
new_directory()
start = time.ticks_ms()

while True:
    # if the timer reaches 30 seconds, pick a new directory
    if time.ticks_diff(time.ticks_ms(), start) > GIF_INTERVAL * 1000:
        new_directory()
        start = time.ticks_ms()
    else:
        for file in files:
            if file.endswith(".png" or ".PNG"):
                img = dir + "/" + file
                p.open_file(img)
                # Decode our PNG file and set the X and Y
                p.decode(0, 0)
                i75.update()
                time.sleep(FRAME_INTERVAL)
