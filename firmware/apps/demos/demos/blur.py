import math

def update():
  star = shape.star(0, 0, 5, 7.5, 12.5)
  star.transform = mat3().translate(screen.width // 2, screen.height // 2).rotate(badge.ticks / 10)
  screen.shape(star)
  screen.antialias = image.X4

  b = math.sin(badge.ticks / 500) * 2 + 2
  screen.blur(b)
