import time
from interstate75 import Interstate75, DISPLAY_INTERSTATE75_256X64

# Setup for the display
i75 = Interstate75(display=DISPLAY_INTERSTATE75_256X64, stb_invert=False, panel_type=Interstate75.PANEL_GENERIC)
display = i75.display

WIDTH, HEIGHT = display.get_bounds()
CY = HEIGHT // 2

# Text we're going to be scrolling. You can change this! :)
TEXT = "Hello there! I am a LOOOOOOOOONG string of text!"
TEXT_SIZE = display.measure_text(TEXT, 5)

# Pens
WHITE = display.create_pen(255, 255, 255)
BLACK = display.create_pen(0, 0, 0)

# Initial position for X places the entire string off screen on the right side.
text_x = WIDTH
text_y = CY - 16

while True:

    # Clear the screen
    display.set_pen(BLACK)
    display.clear()

    # Draw the text in the current position.
    display.set_pen(WHITE)
    display.text(TEXT, text_x, text_y, WIDTH * TEXT_SIZE, 5)

    # Check the position of the text and reset it if it's finished scrolling left
    if text_x + TEXT_SIZE < 0:
        text_x = WIDTH
    else:
        text_x -= 1

    i75.update()
    time.sleep(0.015)
