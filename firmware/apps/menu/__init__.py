import os
import sys

sys.path.insert(0, "/system/apps/menu")
sys.path.insert(0, "/")
os.chdir("/system/apps/menu")

from badgeware import run, set_brightness, is_charging, get_battery_level
from app import Apps
import math


set_brightness(0.2)
screen.font = pixel_font.load("/system/assets/fonts/ark.ppf")

# find installed apps and create apps
apps = Apps("/system/apps")

io.poll()


def draw_battery(level):

    screen.pen = color.rgb(100, 100, 100)
    # draw the battery indicator
    size = (5, 3)
    pos = (screen.width - (size[0] + 1), 0)
    screen.shape(shape.rectangle(*pos, *size))
    screen.put(pos[0] + size[0], pos[1] + 1)
    screen.pen = color.black
    screen.shape(shape.rectangle(pos[0] + 1, pos[1] + 1, size[0] - 2, size[1] - 2))

    # draw the battery fill level
    screen.pen = color.rgb(100, 100, 100)
    width = ((size[0] - 1) / 100) * level
    screen.shape(shape.rectangle(pos[0] + 1, pos[1] + 2, width, size[1] - 4))



def update():
    global show_battery_level

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

    if io.BUTTON_HOME in io.pressed:
        show_battery_level = io.ticks

    if is_charging():
        draw_battery((io.ticks / 20) % 100)
    elif get_battery_level() <=35:
        if int(math.sin(io.ticks / 250) + 1):
            draw_battery(0)

    # draw menu apps
    return apps.draw()


if __name__ == "__main__":
    run(update)
