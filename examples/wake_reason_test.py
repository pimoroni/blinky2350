import blinky
from picographics import PicoGraphics, DISPLAY_GENERIC
import powman
import machine

# Make linter happy
SWITCH_INT = machine.Pin(0)

# Pull all of the machine.Pin.board.LABEL definitions into the local scope
# Note The firmware (via powman startup) will guarantee these are configured.
locals().update(machine.Pin.board.__dict__)

blinky = blinky.Blinky()
display = PicoGraphics(DISPLAY_GENERIC, width=blinky.WIDTH, height=blinky.HEIGHT)

WHITE = display.create_pen(16, 16, 16)
BLACK = display.create_pen(0, 0, 0)

display.set_pen(BLACK)
display.clear()
display.set_pen(WHITE)


wake_reason = powman.get_wake_reason()

if wake_reason == powman.WAKE_BUTTON_A:
    display.text("A", 0, 0)

if wake_reason == powman.WAKE_BUTTON_B:
    display.text("B", 0, 0)

if wake_reason == powman.WAKE_BUTTON_C:
    display.text("C", 0, 0)

if wake_reason == powman.WAKE_BUTTON_UP:
    display.text("Up", 0, 0)

if wake_reason == powman.WAKE_BUTTON_DOWN:
    display.text("Dn", 0, 0)

if wake_reason == powman.WAKE_RTC:
    display.text("RTC", 0, 0)

if wake_reason == powman.WAKE_UNKNOWN:
    display.text("Rst", 0, 0)


display.text(f"{wake_reason}", 0, 12)

blinky.update(display)


def intr(pin):
    if pin.value() == 0:
        powman.sleep()


SWITCH_INT.irq(intr)

while True:
    pass

