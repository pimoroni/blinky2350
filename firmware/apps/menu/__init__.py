import sys
import os

sys.path.insert(0, "/system/apps/menu")
os.chdir("/system/apps/menu")

import math
from badgeware import is_dir, file_exists, run, set_brightness
from icon import Icon
import ui

set_brightness(0.2)

# define the list of installed apps
#
# - hack them!
# - replace them with your own
# - reorder them
# - what would mona do...?
apps = [
    ("mona's quest", "quest"),
    ("mona pet", "monapet"),
    ("monasketch", "sketch"),
    ("flappy mona", "flappy"),
    ("gallery", "gallery"),
    ("badge", "badge"),
]

mona = SpriteSheet("/system/assets/mona-sprites/mona-default.png", 11, 1)
screen.font = rom_font.ark
# screen.antialias = Image.X2

cx, cy = int(screen.width / 2), int(screen.height / 2)

# find installed apps and create icons
icons = []
for app in apps:
    name, path = app[0], app[1]

    if is_dir(f"/system/apps/{path}"):
        if file_exists(f"/system/apps/{path}/icon.png"):
            x = cx + 1
            y = cy
            pos = (x, y)
            sprite = image.load(f"/system/apps/{path}/icon.png")
            icons.append(Icon(pos, name, len(icons), sprite))

active = 0

MAX_ALPHA = 255
alpha = 30


def update():
    global active, icons, alpha

    # process button inputs to switch between icons
    if io.BUTTON_C in io.pressed:
        active += 1
    if io.BUTTON_A in io.pressed:
        active -= 1
#     if io.BUTTON_UP in io.pressed:
#         active -= 3
#     if io.BUTTON_DOWN in io.pressed:
#         active += 3
    if io.BUTTON_B in io.pressed:
        return f"/system/apps/{apps[active][1]}"
    active %= len(icons)

    ui.draw_background()
    ui.draw_header()

    # draw menu icons
    for i in range(len(icons)):
        icons[i].activate(active == i)
#         icons[i].draw()

    # draw label for active menu icon
    if Icon.active_icon:
        icons[active].draw()
        label = f"{Icon.active_icon.name}"
        w, _ = screen.measure_text(label)
        screen.pen = color.rgb(211, 250, 55)
#         screen.shape(shape.rounded_rectangle(cx - (w / 2) - 4, screen.height - 20, w + 8, 15, 4))
        screen.pen = color.rgb(0, 0, 0, 150)
#         screen.text(label, 0, 0)

    if alpha <= MAX_ALPHA:
        screen.pen = color.rgb(0, 0, 0, 255 - alpha)
        screen.clear()
        alpha += 30

    return None


if __name__ == "__main__":
    run(update)
