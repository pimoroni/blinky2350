import os
import sys

sys.path.insert(0, "/system/apps/menu")
sys.path.insert(0, "/")
os.chdir("/system/apps/menu")

# Supersample the menu so icon slides/bobs move smoothly across the panel
badge.mode(SS_X4)

from badgeware import set_brightness
from app import Apps
import math


set_brightness(0.2)
screen.font = font.ark

# Pixel dimensions the menu draws in are multiplied by the supersample factor
SCALE = display.SCALE

# find installed apps and create apps
apps = Apps("/system/apps")

badge.poll()


def draw_battery(level):

    screen.pen = color.rgb(100, 100, 100)
    # draw the battery indicator
    size = (5 * SCALE, 3 * SCALE)
    pos = (screen.width - (size[0] + SCALE), 0)
    screen.shape(shape.rectangle(*pos, *size))
    screen.put(pos[0] + size[0], pos[1] + SCALE)
    screen.pen = color.black
    screen.shape(shape.rectangle(pos[0] + SCALE, pos[1] + SCALE, size[0] - 2 * SCALE, size[1] - 2 * SCALE))

    # draw the battery fill level
    screen.pen = color.rgb(100, 100, 100)
    width = ((size[0] - SCALE) / 100) * level
    screen.shape(shape.rectangle(pos[0] + SCALE, pos[1] + 2 * SCALE, width, size[1] - 4 * SCALE))



def update():
    global show_battery_level

    screen.pen = color.black
    screen.clear()

    # process button inputs to switch between apps
    if badge.pressed(BUTTON_C):
        apps.next()
        print(apps.active.name)
    if badge.pressed(BUTTON_A):
        apps.prev()
        print(apps.active.name)

    if badge.pressed(BUTTON_B):
        apps.launch()

    if badge.pressed(BUTTON_HOME):
        show_battery_level = badge.ticks

    if badge.is_charging():
        draw_battery((badge.ticks / 20) % 100)
    elif badge.battery_level() <=35:
        if int(math.sin(badge.ticks / 250) + 1):
            draw_battery(0)

    # draw menu apps
    return apps.draw()


on_exit = run(update).result
