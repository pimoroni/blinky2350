import machine
import powman
from picographics import PicoGraphics, DISPLAY_GENERIC, PEN_RGB888
from blinky import Blinky


# We can rely on these having been set up by powman... maybe
BUTTON_DOWN = machine.Pin.board.BUTTON_DOWN
BUTTON_A = machine.Pin.board.BUTTON_A
BUTTON_B = machine.Pin.board.BUTTON_B
BUTTON_C = machine.Pin.board.BUTTON_C
BUTTON_UP = machine.Pin.board.BUTTON_UP
BUTTON_HOME = machine.Pin.board.BUTTON_HOME


WIDTH = 39
HEIGHT = 26

SYSTEM_FREQS = [
    4000000,
    12000000,
    48000000,
    133000000,
    250000000
]

BUTTONS = (
    BUTTON_DOWN,
    BUTTON_A,
    BUTTON_B,
    BUTTON_C,
    BUTTON_UP,
    BUTTON_HOME
)


def is_wireless():
    return True


def woken_by_button():
    return powman.get_wake_reason() in (
        powman.WAKE_BUTTON_A,
        powman.WAKE_BUTTON_B,
        powman.WAKE_BUTTON_C,
        powman.WAKE_BUTTON_UP,
        powman.WAKE_BUTTON_DOWN)


def pressed_to_wake(button):
    # TODO: BUTTON_HOME cannot be a wake button
    # so maybe raise an exception
    return button in powman.get_wake_buttons()


def woken_by_reset():
    return powman.get_wake_reason() == 255


def system_speed(speed):
    try:
        machine.freq(SYSTEM_FREQS[speed])
    except IndexError:
        pass


class Blinky2350():
    def __init__(self):

        self.blinky = Blinky()
        self.display = PicoGraphics(display=DISPLAY_GENERIC,
                                    width=self.blinky.WIDTH,
                                    height=self.blinky.HEIGHT,
                                    pen_type=PEN_RGB888)

    def __getattr__(self, item):
        # Glue to redirect calls to PicoGraphics
        return getattr(self.display, item)

    def update(self):
        self.blinky.update(self.display)

    def pressed(self, button):
        return button.value() == 0

    def pressed_any(self):
        return 0 in [button.value() for button in BUTTONS]

    def sleep(self):
        powman.sleep()
