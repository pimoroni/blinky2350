import random
import math

def update():
  random.seed(0)

  for i in range(12):
    x = math.sin(i + badge.ticks / 500) * 8
    y = math.cos(i + badge.ticks / 500) * 8
    p1 = vec2(x + rnd(-10, screen.width + 10), y + rnd(-10, screen.height + 10))
    p2 = vec2(x + rnd(-10, screen.width + 10), y + rnd(-10, screen.height + 10))
    screen.pen = color.rgb(rnd(255), rnd(255), rnd(255))
    screen.line(p1, p2)
