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


class _run:
    @property
    def ticks(self):
        return badge.ticks - self.start

    @property
    def progress(self):
        return 0 if self.duration is None else self.ticks / self.duration

    def __init__(self, *args, duration=None):
        self.start = 0
        self.result = None
        self.duration = duration
        if len(args) == 1 and callable(args[0]):
            self(args[0])

    def __call__(self, update):
        badge.poll()
        self.start = badge.ticks
        parent = loop
        builtins.loop = self

        try:
            while True:
                badge.clear()

                if (result := update()) is not None:
                    self.result = result
                    return

                display.update()
                badge.poll()

                if self.duration is not None and self.ticks >= self.duration:
                    return

        finally:
            badge.clear()
            builtins.loop = parent


def launch(path):
    app = None

    def do_exit():
        on_exit = getattr(app, "on_exit", None)
        return on_exit() if callable(on_exit) else on_exit

    def quit_to_launcher(_pin):
        do_exit()
        reset()

    machine.Pin.board.BUTTON_HOME.irq(
        trigger=machine.Pin.IRQ_FALLING, handler=quit_to_launcher
    )

    # Grab a list of modules from before launching app
    modules_before_launch = list(sys.modules.keys())

    try:
        os.chdir(path)
        sys.path.insert(0, path)
        app = __import__(path)  # App may block here

        return do_exit()

    except Exception as e:  # noqa: BLE001
        fatal_error("Error!", get_exception(e))

    finally:
        # Clean up path
        if sys.path[0].startswith("/system/apps"):
            sys.path.pop(0)

        # Clean up any imported modules
        for key in sys.modules.keys():
            if key not in modules_before_launch:
                del sys.modules[key]

        gc.collect()



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
builtins.run = _run
builtins.launch = launch
builtins.loop = None
builtins.reset = reset
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
