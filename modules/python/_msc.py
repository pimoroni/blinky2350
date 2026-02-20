from badgeware import run
import rp2

import binascii
import uctypes


# Disarm the home button to help mitigate unwanted resets in MSC mode
BUTTON_HOME.irq(None)


# Get a CRC of the FAT (first 16k of the user filesystem) ~16ms
CACHE_FILE = "/.fsbackup"

fat = uctypes.bytearray_at(0x10300000, 16 * 1024)
crc = f"{binascii.crc32(fat):08x}"

try:
    cached_crc = open(f"{CACHE_FILE}.crc32", "r").read().strip()
except OSError:
    cached_crc = ""

if cached_crc != crc:
    with open(f"{CACHE_FILE}.crc32", "w") as f:
        f.write(crc)
        f.flush()
    with open(CACHE_FILE, "wb") as f:
        f.write(fat)
        f.flush()

rp2.enable_msc()

background = color.rgb(0, 0, 0)
white = color.rgb(35, 41, 37)

try:
    small_font = rom_font.winds
except OSError:
    small_font = None


class DiskMode():
    def __init__(self):
        self.transferring = False

    def draw(self):
        screen.pen = background
        screen.clear()

        if small_font:
            screen.font = small_font
            screen.pen = white
            center_text("USB", 0)

            screen.pen = white
            if self.transferring:
                center_text("<<<", 7)
            else:
                center_text("waiting", 7)


def center_text(text, y):
    w, h = screen.measure_text(text)
    screen.text(text, (screen.width / 2) - (w / 2), y)


def wrap_text(text, x, y):
    lines = text.splitlines()
    for line in lines:
        _, h = screen.measure_text(line)
        screen.text(line, x, y)
        y += h * 0.8


disk_mode = DiskMode()


def update():
    # set transfer state here
    disk_mode.transferring = rp2.is_msc_busy()

    badge.caselights(int(disk_mode.transferring))

    # draw the ui
    disk_mode.draw()


run(update)
