import math
import random

def update():
  random.seed(0)
  for i in range(12):
    x = math.sin(i + badge.ticks / 100) * 8
    y = math.cos(i + badge.ticks / 100) * 8

    p = vec2(x + rnd(screen.width), y + rnd(screen.height))
    p1 = vec2(p.x + rnd(-7, 7), p.y + rnd(-7, 7))
    p2 = vec2(p.x + rnd(-7, 7), p.y + rnd(-7, 7))
    p3 = vec2(p.x + rnd(-7, 7), p.y + rnd(-7, 7))

    screen.pen = color.rgb(rnd(255), rnd(255), rnd(255))
    screen.triangle(p1, p2, p3)
