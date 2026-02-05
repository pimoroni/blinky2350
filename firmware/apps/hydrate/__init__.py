import sys
import os

sys.path.insert(0, "/system/apps/hydrate")
os.chdir("/system/apps/hydrate")

from badgeware import State, set_brightness

CX = screen.width / 2
CY = screen.height / 2

state = {
    "current": 0,
    "goal": 2000
}

screen.antialias = image.X4
set_brightness(0.1)

large_font = pixel_font.load("/system/assets/fonts/smart.ppf")
screen.font = large_font


def goal_met():
    return state["current"] >= state["goal"]


def draw_graph(value):

    # map the value to a range that matches the display height
    v = (((value - 0) * (screen.height - 1)) / (state["goal"] - 0)) + 1

    # text and measurements for centring
    text = f"{state["current"]}ml"
    tw, _ = screen.measure_text(text)
    tx = CX - (tw / 2)

    # we're drawing the text twice here, once in black and once in white, with clipping
    # based on the water level
    screen.pen = color.white
    screen.text(text, vec2(tx, CY - 8))
    screen.rectangle(CX - 3, screen.height - 5, 7, 7)
    screen.pen = color.white
    screen.clip = rect(0, screen.height - v, screen.width, v)
    screen.clear()
    screen.pen = color.black
    screen.text(text, vec2(tx, CY - 8))
    screen.pen = color.rgb(70, 70, 70)
    screen.rectangle(CX - 3, screen.height - 5, 7, 7)

    # set the clip back to full screen
    screen.clip = rect(0, 0, screen.width, screen.height)


show_menu = False
menu_value = 0


def draw_menu():
    global show_menu, menu_value

    # darken the background when the menu is showing
    if show_menu:
        screen.pen = color.black
        screen.clear()

    # draw the menu background
    screen.pen = color.black
    screen.clear()

    # Show the menu elements if the menu is showing including during transition
    screen.pen = color.white
    text = f"{menu_value}ml"
    tw, _ = screen.measure_text(text)
    tx = CX - (tw / 2)
    screen.text(text, tx, CY - 10)

    screen.text("-", vec2(8, screen.height - 14))
    screen.text("+", vec2(26, screen.height - 14))
    screen.rectangle(screen.width - 5, 12, 7, 7)


def init():
    global state
    State.load("hydrate", state)


def update():
    global state, show_menu, menu_value

    if badge.pressed(BUTTON_B):
        show_menu = not show_menu

    if show_menu:

        draw_menu()

        # increase/decrease the value to add
        # short press is +/- 5ml and long is +/- 25ml
        if badge.pressed(BUTTON_A):
            menu_value -= 50
        if badge.pressed(BUTTON_C):
            menu_value += 50

        if badge.pressed(BUTTON_DOWN):
            state["current"] += menu_value
            menu_value = 0
            show_menu = not show_menu
            State.save("hydrate", state)

        if badge.held(BUTTON_UP):
            state["current"] = 0
            State.save("hydrate", state)

        menu_value = clamp(menu_value, 0, state["goal"])

    else:
        screen.pen = color.black
        screen.clear()

        draw_graph(state["current"])


def on_exit():
    pass


if __name__ == "__main__":
    run(update, init=init, on_exit=on_exit)
