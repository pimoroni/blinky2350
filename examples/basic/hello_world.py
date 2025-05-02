"""
Bitmap font demo!

Bitmap fonts are fast but blocky. They are best used for small text.
"""

from interstate75 import Interstate75


# if the text does not show as magenta and white, try changing the color_order below
i75 = Interstate75(display=Interstate75.DISPLAY_INTERSTATE75_128X128, color_order=Interstate75.COLOR_ORDER_RGB)
graphics = i75.display

MAGENTA = graphics.create_pen(255, 0, 255)
BLACK = graphics.create_pen(0, 0, 0)
WHITE = graphics.create_pen(255, 255, 255)

while True:
    graphics.set_pen(MAGENTA)
    graphics.text("hello", 1, 0, scale=1)
    graphics.set_pen(WHITE)
    graphics.text("world", 1, 6, scale=1)
    i75.update()
