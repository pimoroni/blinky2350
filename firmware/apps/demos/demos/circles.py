import math
import random

def update():
  random.seed(0)

  for i in range(20):
    x = math.sin(i + badge.ticks / 100) * 8
    y = math.cos(i + badge.ticks / 100) * 8

    p = vec2(x + rnd(screen.width), y + rnd(screen.height))
    r = rnd(1, 5)
    screen.pen = color.rgb(rnd(255), rnd(255), rnd(255))
    screen.circle(p, r)
