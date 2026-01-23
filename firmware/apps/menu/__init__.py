import os
import sys

sys.path.insert(0, "/system/apps/menu")
sys.path.insert(0, "/")
os.chdir("/system/apps/menu")

from badgeware import run, set_brightness
from app import Apps


set_brightness(0.2)
screen.font = pixel_font.load("/system/assets/fonts/ark.ppf")

# find installed apps and create apps
apps = Apps("/system/apps")


def update():

    screen.pen = color.black
    screen.clear()

    # process button inputs to switch between apps
    if io.BUTTON_C in io.pressed:
        apps.next()
        print(apps.active.name)
    if io.BUTTON_A in io.pressed:
        apps.prev()
        print(apps.active.name)

    if io.BUTTON_B in io.pressed:
        apps.launch()

    # draw menu apps
    return apps.draw()


if __name__ == "__main__":
    run(update)
