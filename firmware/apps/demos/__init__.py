import os
import sys

APP_DIR = "/system/apps/demos"

sys.path.insert(0, APP_DIR)
os.chdir(APP_DIR)

from badgeware import run, BG

mode(LORES)


import gc, sys

sins = rom_font.sins

from demos import demos
names = sorted(demos.keys())

selected = None
menu_index = 0
demo = None

def load_demo(index):
  global selected, demo

  # unload previously running demo
  if demo:
    del sys.modules[f"{APP_DIR}/demos/{names[selected]}"]

  gc.collect()

  selected = index
  selected %= len(names)

  name = names[selected]
  demo = __import__(demos[name])

  print(f"loaded example {name} ({round(gc.mem_free() / 1000)}KB free)")

selected = 0
load_demo(0)

def update():
  global selected, menu_index

  if io.BUTTON_DOWN in io.pressed:
    load_demo(selected + 1)

  if io.BUTTON_UP in io.pressed:
    load_demo(selected - 1)

  # make sure a font is loaded by default in case the example wishes to use it
  screen.font = sins

  # call example update function
  demo.update()

  # restore font for our use in case demo overrode it
  screen.font = sins

  if menu_index < selected:
    menu_index += (selected - menu_index) / 20
  if menu_index > selected:
    menu_index -= (menu_index - selected) / 20

  # render 5 items above the current item, and 1 below, fade out from current
  for i in range(0, len(names)):
    name = names[i]

    y = 102 + (i * 10) - menu_index * 10
    alpha = abs(y) / 3
    if i == selected:
      screen.pen = color.rgb(20, 40, 60, 255)
      w, h = screen.measure_text(name)
      screen.rectangle(3, y + 2, w + 4, h - 2)

      screen.pen = color.rgb(255, 255, 255, 255)
      screen.text(name, 5, y)
    else:
      screen.pen = color.rgb(20, 40, 60, alpha)
      w, h = screen.measure_text(name)
      screen.rectangle(3, y + 2, w + 4, h - 2)

      screen.pen = color.rgb(255, 255, 255, alpha)
      screen.text(name, 5, y)


if __name__ == "__main__":
    AVERAGE_OVER = 60
    SAMPLE_COUNT = 5

    frames = 0
    total = 0
    samples = 0
    next_test = False
    current_test = names[selected]

    import time

    freq = machine.freq() / 1_000_000

    while True:
        screen.pen = BG
        screen.clear()
        io.poll()

        t_start = time.ticks_ms()
        next_test = update()
        diff = time.ticks_diff(time.ticks_ms(), t_start)
        bw.display.update(screen.width == 320)
        total += diff
        frames += 1

        if next_test != current_test:
            current_test = next_test
            total = 0
            frames = 0
            samples = 0

        if frames == AVERAGE_OVER:
            samples += 1
            avg_frame_time = total / frames
            avg_fps = 1000 / avg_frame_time
            print(f"{current_test}: {samples}: {avg_frame_time:.02f}ms {avg_fps:.02f}fps averaged over {frames} frames at {freq:.2f}MHz")
            frames = 0
            total = 0
            if samples == SAMPLE_COUNT:
                samples = 0
                next_demo = True



