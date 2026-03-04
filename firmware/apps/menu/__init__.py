import os
import sys

sys.path.insert(0, "/system/apps/menu")
sys.path.insert(0, "/")
os.chdir("/system/apps/menu")

from badgeware import set_brightness
from app import Apps
import math
import qwstpad


set_brightness(0.2)
screen.font = pixel_font.load("/system/assets/fonts/ark.ppf")

# find installed apps and create apps
apps = Apps("/system/apps")

badge.poll()
gamepad = None
controls = {}


def init_gamepad():
    global gamepad
    gamepads = qwstpad.Gamepadhelper()
    for i in gamepads.pads:
        if i is not None:
            gamepad = i
            return i
    return None


def parse_controls():
    global controls, gamepad

    if not gamepad:
        gamepad = init_gamepad()

    if gamepad:
        try:
            gamepad.update_buttons()
        except OSError:
            gamepad = init_gamepad()

    if gamepad:
        controls["LEFT"] = badge.pressed(BUTTON_A) or gamepad.pressed("L")
        controls["RIGHT"] = badge.pressed(BUTTON_C) or gamepad.pressed("R")
        controls["SELECT"] = badge.pressed(BUTTON_B) or gamepad.pressed("B")
        controls["BATTERY"] = badge.pressed(BUTTON_HOME) or gamepad.pressed("+")
    else:
        controls["LEFT"] = badge.pressed(BUTTON_A)
        controls["RIGHT"] = badge.pressed(BUTTON_C)
        controls["SELECT"] = badge.pressed(BUTTON_B)
        controls["BATTERY"] = badge.pressed(BUTTON_HOME)


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

    parse_controls()

    screen.pen = color.black
    screen.clear()

    # process button inputs to switch between apps
    if controls["RIGHT"]:
        apps.next()
        print(apps.active.name)
    if controls["LEFT"]:
        apps.prev()
        print(apps.active.name)

    if controls["SELECT"]:
        apps.launch()

    if controls["BATTERY"]:
        show_battery_level = badge.ticks

    if badge.is_charging():
        draw_battery((badge.ticks / 20) % 100)
    elif badge.battery_level() <=35:
        if int(math.sin(badge.ticks / 250) + 1):
            draw_battery(0)

    # draw menu apps
    return apps.draw()


on_exit = run(update).result
