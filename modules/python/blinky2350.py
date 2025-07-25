import cppmem
import machine
import powman
from picographics import PicoGraphics, DISPLAY_GENERIC, PEN_RGB888
from blinky import Blinky
import micropython

BUTTON_DOWN = 6
BUTTON_A = 7
BUTTON_B = 8
BUTTON_C = 9
BUTTON_UP = 10
BUTTON_USER = 22

BUTTON_MASK = 0b11111 << 11

WIDTH = 39
HEIGHT = 26

SYSTEM_FREQS = [
    4000000,
    12000000,
    48000000,
    133000000,
    250000000
]

BUTTONS = {
    BUTTON_DOWN: machine.Pin(BUTTON_DOWN, machine.Pin.IN, machine.Pin.PULL_UP),
    BUTTON_A: machine.Pin(BUTTON_A, machine.Pin.IN, machine.Pin.PULL_UP),
    BUTTON_B: machine.Pin(BUTTON_B, machine.Pin.IN, machine.Pin.PULL_UP),
    BUTTON_C: machine.Pin(BUTTON_C, machine.Pin.IN, machine.Pin.PULL_UP),
    BUTTON_UP: machine.Pin(BUTTON_UP, machine.Pin.IN, machine.Pin.PULL_UP),
}


cppmem.set_mode(cppmem.MICROPYTHON)


def is_wireless():
    return True


def woken_by_button():
    return powman.get_wake_reason() in [0, 1, 2]


def pressed_to_wake(button):
    try:
        return [7, 8, 9].index(button) == powman.get_wake_reason()
    except ValueError:
        raise KeyError("Button not valid for device wake function!") from None


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

    def invert(self, _invert):
        raise RuntimeError("Display invert not supported in PicoGraphics.")

    def thickness(self, _thickness):
        raise RuntimeError("Thickness not supported in PicoGraphics.")

    def pressed(self, button):
        return BUTTONS[button].value() == 0

    def pressed_any(self):
        for button in BUTTONS.values():
            if button.value() == 0:
                return True
        return False

    @micropython.native
    def icon(self, data, index, data_w, icon_size, x, y):
        s_x = (index * icon_size) % data_w
        s_y = int((index * icon_size) / data_w)

        for o_y in range(icon_size):
            for o_x in range(icon_size):
                o = ((o_y + s_y) * data_w) + (o_x + s_x)
                bm = 0b10000000 >> (o & 0b111)
                if data[o >> 3] & bm:
                    self.display.pixel(x + o_x, y + o_y)

    def image(self, data, w, h, x, y):
        for oy in range(h):
            row = data[oy]
            for ox in range(w):
                if row & 0b1 == 0:
                    self.display.pixel(x + ox, y + oy)
                row >>= 1

    def sleep(self):
        powman.goto_dormant_until_pin(None, False, False)
