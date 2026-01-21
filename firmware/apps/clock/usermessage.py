black = color.rgb(0, 0, 0)
white = color.rgb(255, 255, 255)
small_font = rom_font.winds


def center_text(text, y):
    # Centre text on screen

    w, h = screen.measure_text(text)
    screen.text(text, (screen.width / 2) - (w / 2), y)


def user_message(caption, line1):
    # A simple message screen with a single line of text.

    screen.pen = black
    screen.clear()
    screen.font = small_font
    screen.pen = white
    center_text(caption, 1)

    screen.font = small_font
    center_text(line1, 9)
