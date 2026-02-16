import gc
from io import StringIO
import sys
import os

import machine
import blinky
import builtins

import picovector


def set_brightness(value):
    display.set_brightness(value)


def reset():
    # HOME is also BOOT; if we reset while it's
    # low we'll end up in bootloader mode.
    while not machine.Pin.board.BUTTON_HOME.value():
        pass
    machine.reset()


def run(update, init=None, on_exit=None):
    modules_before_launch = list(sys.modules.keys())
    try:
        screen.font = DEFAULT_FONT

        if isinstance(update, str):
            path = update
            os.chdir(path)
            sys.path.insert(0, path)
            app = __import__(path)
            update = app.update
            init = getattr(app, "init", None)
            on_exit = getattr(app, "on_exit", None)

        def do_exit():
            if on_exit:
                on_exit()

            # Clean up path
            if sys.path[0].startswith("/system/apps"):
                sys.path.pop(0)

            # Clean up any imported modules
            for key in sys.modules.keys():
                if key not in modules_before_launch:
                    del sys.modules[key]

            gc.collect()

        def quit_to_launcher(_pin):
            do_exit()
            reset()

        machine.Pin.board.BUTTON_HOME.irq(
            trigger=machine.Pin.IRQ_FALLING, handler=quit_to_launcher
        )

        if badge.default_clear is None:
            screen.pen = color.black
            screen.clear()

        if init:
            init()
            gc.collect()

        while True:
            if badge.default_clear is not None:
                screen.pen = badge.default_clear
                screen.clear()
            screen.pen = badge.default_pen

            badge.poll()
            if (result := update()) is not None:
                return result

            display.update()

    except Exception as e:  # noqa: BLE001
        fatal_error("Error!", get_exception(e))

    finally:
        do_exit()


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

    update_text = text.scroll(f"{title}: {error}")

    while True:
        screen.pen = color.black
        screen.clear()
        screen.pen = color.white
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
badge.default_pen = color.white
badge.default_clear = color.black
