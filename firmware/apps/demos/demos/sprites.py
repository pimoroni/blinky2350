import random
import math

skull = image.load("/system/assets/skull.png")

def update():
  random.seed(0)
  for i in range(5):
    s = (math.sin(badge.ticks / 500 + i / 5) * 1) + 1

    skull.alpha = int((math.sin((badge.ticks + i * 30) / 500) + 1) * 127)

    x = math.sin(i + badge.ticks / 1000) * (screen.width / 2)
    y = math.cos(i + badge.ticks / 1000) * (screen.height / 2)

    pos = vec2(x + rnd(-20, 20), y + rnd(-20, 20))

    dr = rect(
      pos.x, pos.y, (16 * s) + 2, (12 * s) + 2
    )
    screen.blit(skull, dr)
