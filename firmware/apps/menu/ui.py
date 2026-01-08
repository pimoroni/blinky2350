
black = color.rgb(0, 0, 0)
background = black
phosphor = color.rgb(211, 250, 55)
terminal_text = color.rgb(60, 71, 16)
terminal_fade = color.rgb(35, 41, 37, 150)


def draw_background():
    screen.pen = black
    screen.clear()


def draw_header():
    pass
    # create animated header text
#     dots = "." * int(math.sin(io.ticks / 250) * 2 + 2)
#     label = f"Mona-OS v4.03{dots}"
#     pos = (5, 2)

    # draw the OS title
#     screen.pen = phosphor
#     screen.text(label, *pos)
#
#     # draw the battery indicator
#     if is_charging():
#         battery_level = (io.ticks / 20) % 100
#     else:
#         battery_level = get_battery_level()
#     pos = (137, 4)
#     size = (16, 8)
#     screen.pen = phosphor
#     screen.shape(shape.rectangle(*pos, *size))
#     screen.shape(shape.rectangle(pos[0] + size[0], pos[1] + 2, 1, 4))
#     screen.pen = background
#     screen.shape(shape.rectangle(pos[0] + 1, pos[1] + 1, size[0] - 2, size[1] - 2))
#
#     # draw the battery fill level
#     width = ((size[0] - 4) / 100) * battery_level
#     screen.pen = phosphor
#     screen.shape(shape.rectangle(pos[0] + 2, pos[1] + 2, width, size[1] - 4))
