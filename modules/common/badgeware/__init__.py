import gc
from io import StringIO
import sys

import machine
import blinky
import builtins

import picovector


def set_brightness(value):
    display.set_brightness(value)


def run(update, init=None, on_exit=None):
    screen.font = DEFAULT_FONT
    screen.pen = color.black
    screen.clear()
    screen.pen = badge.default_pen()
    try:
        if init:
            init()
            gc.collect()
        try:
            while True:
                if badge.default_clear() is not None:
                    screen.pen = badge.default_clear()
                    screen.clear()
                screen.pen = badge.default_pen()
                badge.poll()
                if (result := update()) is not None:
                    gc.collect()
                    return result
                display.update()
        finally:
            if on_exit:
                on_exit()
                gc.collect()

    except Exception as e:  # noqa: BLE001
        fatal_error("Error!", get_exception(e))


def get_exception(e):
    s = StringIO()
    sys.print_exception(e, s)
    s.seek(0)
    s.readline()  # Drop the "Traceback" bit
    return s.read()


def fatal_error(title, error):
    if not isinstance(error, str):
        error = get_exception(error)
    print(f"- ERROR: {error}")

    screen.pen = color.black
    screen.clear()

    badge.poll()

    update_text = text.scroll(f"{title}: {error}", bg=color.black)

    while True:
        badge.poll()
        update_text()
        if badge.pressed():
            break
        display.update()

    while badge.pressed():
        badge.poll()

    machine.reset()


display = blinky.Blinky()

# Import PicoSystem module constants to builtins,
# so they are available globally.
for k, v in picovector.__dict__.items():
    if not k.startswith("__"):
        setattr(builtins, k, v)

# Hoist image anti-aliasing constants
builtins.OFF = image.OFF
builtins.X2 = image.X2
builtins.X4 = image.X4

# Hoist display and run for clean Thonny apps
builtins.display = display
builtins.run = run
builtins.fatal_error = fatal_error

# Import badgeware modules
__import__(".frozen/badgeware/badge")
__import__(".frozen/badgeware/math")
__import__(".frozen/badgeware/text")
__import__(".frozen/badgeware/sprite")
__import__(".frozen/badgeware/filesystem")
__import__(".frozen/badgeware/memory")
__import__(".frozen/badgeware/rtc")
State = __import__(".frozen/badgeware/state").State

DEFAULT_FONT = rom_font.sins

badge.mode(LORES)
badge.default_pen(color.white)
badge.default_clear(color.black)
