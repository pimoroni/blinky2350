import os
import sys
from badgeware import set_brightness

sys.path.insert(0, "/system/apps/gallery")
os.chdir("/system/apps/gallery")

screen.font = rom_font.sins
screen.antialias = image.X2

set_brightness(0.2)

ui_hidden = False

files = []
total_files = len(os.listdir("images"))

if total_files == 0:
    fatal_error("No images found!", "Enter disk mode and copy your PNGs to /apps/gallery/images")

bar_width = screen.width - 2
bar_x = (screen.width // 2) - (bar_width // 2)
segment_width = (bar_width // total_files)


def center_text(text, y):
    w, _ = screen.measure_text(text)
    screen.text(text, (screen.width / 2) - (w / 2), y)


# create a dictionary of all the images in the images directory
for i, file in enumerate(os.listdir("images")):
    screen.pen = color.black
    screen.clear()
    screen.pen = color.white

    center_text("Loading", 1)

    screen.shape(shape.rectangle(bar_x, (screen.height // 2) + 1, bar_width, 5).stroke(2))
    screen.shape(shape.rectangle((bar_x - segment_width) + segment_width, (screen.height // 2) + 1, segment_width * i, 5))

    file = file.rsplit("/", 1)[-1]
    name, ext = file.rsplit(".", 1)
    if ext == "png":
        files.append({
            "name": file,
            "title": name.replace("-", " "),
            "image": image.load(f"images/{name}.png")
        })

    display.update()


# given a gallery image index it clamps it into the range of available images

def clamp_index(index):
    return index % len(files)


# load the main image based on the gallery index provided
def load_image(index):
    global image
    index = clamp_index(index)
    image = files[index]["image"]


# start up with the first image in the gallery
index = 0
load_image(index)

thumbnail_scroll = index
image_changed_at = None


def update():
    global index, thumbnail_scroll, ui_hidden, image_changed_at

    # if the user presses left or right then switch image
    if badge.pressed(BUTTON_A):
        index -= 1
        ui_hidden = False
        image_changed_at = badge.ticks
        load_image(index)

    if badge.pressed(BUTTON_C):
        index += 1
        ui_hidden = False
        image_changed_at = badge.ticks
        load_image(index)

    if badge.pressed(BUTTON_B):
        ui_hidden = not ui_hidden
        image_changed_at = badge.ticks

    if image_changed_at and (badge.ticks - image_changed_at) > 2000:
        ui_hidden = True

    # draw the currently selected image
    screen.blit(image, rect(0, 0, image.width, image.height), rect(0, 0, screen.width, screen.height))

    title = files[clamp_index(index)]["title"]
    width, _ = screen.measure_text(title)

    if not ui_hidden:

        screen.pen = color.rgb(0, 0, 0, 120)
        screen.shape(shape.rectangle(0, 14, 6, 7))
        screen.shape(shape.rectangle(29, 14, 6, 7))

        screen.pen = color.white
        screen.text("<", 0, 10)
        screen.text(">", 30, 10)


run(update)
