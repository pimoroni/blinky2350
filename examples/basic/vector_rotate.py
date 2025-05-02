"""

Example showing how to draw a rect with rounded corners
and rotate it around the display centre point using Pico Vector.

"""

from interstate75 import Interstate75, DISPLAY_INTERSTATE75_128X128
from picovector import ANTIALIAS_BEST, PicoVector, Transform, Polygon

i75 = Interstate75(display=DISPLAY_INTERSTATE75_128X128)
display = i75.display

WIDTH = i75.width
HEIGHT = i75.height

# Couple of colours for use later
GREEN = display.create_pen(9, 185, 120)
BLACK = display.create_pen(0, 0, 0)

# Pico Vector
vector = PicoVector(display)
vector.set_antialiasing(ANTIALIAS_BEST)

t = Transform()
vector.set_transform(t)

rect = Polygon()

rect_w = 115
rect_h = 50
rect_x = WIDTH // 2 - rect_w // 2
rect_y = HEIGHT // 2 - rect_h // 2

rect.rectangle(rect_x, rect_y, rect_w, rect_h, corners=(5, 5, 5, 5))

while True:

    # Clear the display
    display.set_pen(BLACK)
    display.clear()

    # Set the colour we want our rect to be
    display.set_pen(GREEN)

    # Rotate in 1 degree steps around the centre of the screen
    t.rotate(1, (64, 64))

    # Draw our rect
    vector.draw(rect)

    # Update the display
    i75.update()
