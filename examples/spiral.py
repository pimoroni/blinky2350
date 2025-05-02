from interstate75 import Interstate75, DISPLAY_INTERSTATE75_128X128
import math
import time

i75 = Interstate75(display=DISPLAY_INTERSTATE75_128X128)
display = i75.display

WIDTH = i75.width
HEIGHT = i75.height

BLACK = display.create_pen(0, 0, 0)

# Set the initial pen colour
pen = display.create_pen_hsv(1.0, 1.0, 1.0)
display.set_pen(pen)

n = 0
c = 2

while True:

    # We'll use this for cycling through the rainbow
    t = time.ticks_ms() / 1000

    a = n * 140
    r = c * math.sqrt(n)

    x = int(r * math.cos(a) + WIDTH // 2)
    y = int(r * math.sin(a) + HEIGHT // 2)

    display.circle(x, y, 1)

    # Update the display
    i75.update()

    n += 1

    # The value '1600' is roughly the number of iterations required to fill a 128 x 128 matrix
    if n > 1600:
        # Clear the screen
        display.set_pen(BLACK)
        display.clear()

        # Reset the pen so we can reuse it
        display.reset_pen(pen)

        # Set the new colour based on the ticks
        pen = display.create_pen_hsv(t, 1.0, 1.0)
        display.set_pen(pen)

        # Set variable n back to 0 to start the spiral again
        n = 0
