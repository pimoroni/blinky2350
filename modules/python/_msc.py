from badgeware import screen, brushes, PixelFont
from ssd1680 import SSD1680
import rp2


display = SSD1680()

rp2.enable_msc()

background = brushes.color(235, 245, 255)
white = brushes.color(35, 41, 37)
faded = brushes.color(35, 41, 37, 200)

try:
    small_font = PixelFont.load("/system/assets/fonts/ark.ppf")
    large_font = PixelFont.load("/system/assets/fonts/absolute.ppf")
except OSError:
    small_font = None
    large_font = None

class DiskMode():
  def __init__(self):
    self.transferring = False

  def draw(self):
    screen.brush = background
    screen.clear()

    if large_font:
        screen.font = large_font
        screen.brush = white
        center_text("USB Disk Mode", 5)

        screen.text("1:", 10, 25)
        screen.text("2:", 10, 45)
        screen.text("3:", 10, 65)

        screen.brush = white
        screen.font = small_font
        wrap_text("""Your badge is now mounted as a disk""", 30, 28)

        wrap_text("""Copy code onto it to experiment!""", 30, 48)

        wrap_text("""Eject the disk to reboot your badge""", 30, 68)

        screen.font = small_font
        if self.transferring:
            screen.brush = white
            center_text("Transferring data!", 102)
        else:
            screen.brush = faded
            center_text("Waiting for data", 102)

def center_text(text, y):
  w, h = screen.measure_text(text)
  screen.text(text, 80 - (w / 2), y)

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

  # draw the ui
  disk_mode.draw()


update()
display.update()

while True:
   pass
