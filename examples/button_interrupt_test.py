import machine

# Make linter happy
BUTTON_UP = BUTTON_DOWN = BUTTON_A = BUTTON_B = BUTTON_C = SWITCH_INT = machine.Pin(0)

# Pull all of the machine.Pin.board.LABEL definitions into the local scope
# Note The firmware (via powman startup) will guarantee these are configured.
locals().update(machine.Pin.board.__dict__)


def intr(pin):
    print(f"int = {pin.value()}", end=": ")
    print(f"U = {~BUTTON_UP.value() & 1}", end=", ")
    print(f"D = {~BUTTON_DOWN.value() & 1}", end=", ")
    print(f"A = {~BUTTON_A.value() & 1}", end=", ")
    print(f"B = {~BUTTON_B.value() & 1}", end=", ")
    print(f"C = {~BUTTON_C.value() & 1}")


SWITCH_INT.irq(intr)

while True:
    pass
