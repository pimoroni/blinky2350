import gc
import os
import time
import blinky2350
from picovector import HALIGN_CENTER, PicoVector, Transform
import math

import blinky_os

display = blinky2350.Blinky2350()

ICONS = {
    "badge": "\uea67",
    "book_2": "\uf53e",
    "check_box": "\ue834",
    "cloud": "\ue2bd",
    "deployed-code": "\uf720",
    "description": "\ue873",
    "help": "\ue887",
    "water_full": "\uf6d6",
    "wifi": "\ue63e",
    "image": "\ue3f4",
    "info": "\ue88e",
    "format_list_bulleted": "\ue241",
    "joystick": "\uf5ee",
    "playing_cards": "\uf5dc"
}

APP_DIR = "/examples"
FONT_SIZE = 1

changed = False
transition = False
exited_to_launcher = False

state = {
    "selected_icon": "ebook",
    "running": "launcher",
    "selected_file": 0,
}

blinky_os.state_load("launcher", state)

if state["running"] != "launcher":
    blinky_os.launch(state["running"])

# Colours
BACKGROUND = display.create_pen(0, 0, 0)
FOREGROUND = display.create_pen(100, 100, 100)
HIGHLIGHT = display.create_pen(30, 30, 30)

# Pico Vector
vector = PicoVector(display.display)
t = Transform()
vector.set_font("Roboto-Medium-With-Material-Symbols.af", 20)
vector.set_font_align(HALIGN_CENTER)
vector.set_transform(t)

examples = [x[:-3] for x in os.listdir(APP_DIR) if x.endswith(".py")]

MAX_PER_ROW = 1
MAX_PER_PAGE = 1
ICONS_TOTAL = len(examples)
MAX_PAGE = ICONS_TOTAL

WIDTH, HEIGHT = display.get_bounds()

LEFT_CORNER_LEDS = [(4, HEIGHT - 4)]

# Page layout
CENTRES = [20, 11]

CENTRE_X = WIDTH // 2
CENTRE_Y = HEIGHT // 2


def read_header(label):
    file = f"{APP_DIR}/{label}.py"

    name = label
    icon = ICONS["description"]

    with open(file) as f:
        header = [f.readline().strip() for _ in range(3)]

    for line in header:
        if line.startswith("# ICON "):
            icon = line[7:].strip()
            icon = ICONS[icon]

        if line.startswith("# NAME "):
            name = line[7:]

    return name, icon


def draw_icon(icon, x, y):

    display.set_pen(FOREGROUND)
    vector.set_font_size(10)
    vector.set_transform(t)
    vector.text(icon, x, y)


def launch_transition():

    x, y = CENTRES
    _, icon = read_header(examples[selected_index])

    for i in range(25):
        display.set_pen(BACKGROUND)
        display.clear()

        display.set_pen(FOREGROUND)
        vector.set_font_size(10 + i)
        vector.set_transform(t)
        vector.text(icon, x, y)

        t.reset()
        display.update()
        time.sleep(0.005)

    display.set_pen(BACKGROUND)
    display.clear()
    display.update()


def render(selected_index):
    global transition

    # Bouncy bouncy icons
    ticks = time.ticks_ms() / 1000.0
    bounce = int(math.sin(ticks * 12) * 2)

    display.set_pen(BACKGROUND)
    display.clear()

    # get the names of the previous and current apps
    icon_current = examples[selected_index]
    icon_previous = examples[previous_index]

    x, y = CENTRES
    y += bounce

    _, icon_current = read_header(icon_current)

    # transition from one icon to the next over a period of 100ms
    if transition:
        _, icon_prev = read_header(icon_previous)
        direction = selected_index > previous_index

        for i in range(20):
            display.set_pen(BACKGROUND)
            display.clear()
            display.set_pen(FOREGROUND)

            offset = i * 2
            prev_x = x + offset if direction else x - offset
            curr_x = i if direction else WIDTH - i

            vector.text(icon_prev, prev_x, y)
            vector.text(icon_current, curr_x, y)

            display.update()
            time.sleep(0.005)

        # Set transition to false once the animation has finished.
        transition = False
    else:
        draw_icon(icon_current, x, y)
        display.update()

    gc.collect()


def wait_for_user_to_release_buttons():
    while display.pressed_any():
        time.sleep(0.01)


def launch_example(file):
    wait_for_user_to_release_buttons()
    launch_transition()

    time.sleep(1)

    file = f"{APP_DIR}/{file}"

    for k in locals().keys():
        if k not in ("gc", "file", "blinky_os"):
            del locals()[k]

    gc.collect()

    blinky_os.launch(file)


try:
    selected_index = examples.index(state["selected_file"])
except (ValueError, KeyError):
    selected_index = 0

previous_index = 0

while True:

    if display.pressed(blinky2350.BUTTON_B):
        launch_example(state["selected_file"])

    if display.pressed(blinky2350.BUTTON_C):
        if selected_index >= MAX_PER_PAGE:
            previous_index = selected_index
            selected_index -= MAX_PER_PAGE
            transition = True
            changed = True

    if display.pressed(blinky2350.BUTTON_A):
        if selected_index < ICONS_TOTAL - 1:
            previous_index = selected_index
            selected_index += MAX_PER_PAGE
            selected_index = min(selected_index, ICONS_TOTAL - 1)
            transition = True
            changed = True

    if changed:
        state["selected_file"] = examples[selected_index]
        blinky_os.state_save("launcher", state)
        changed = False
        # wait_for_user_to_release_buttons()

    render(selected_index)
