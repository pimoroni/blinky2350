import math

ORB = [
  (0.0, color.rgb(255, 255, 255)),
  (0.35, color.rgb(120, 210, 255)),
  (1.0, color.rgb(18, 28, 84)),
]


def update():
  screen.antialias = image.X4

  w = screen.width
  h = screen.height
  cx, cy = w * 0.5, h * 0.5
  rad = min(w, h) * 0.55

  # roll the highlight around so the orb reads like a rotating lit sphere
  ang = badge.ticks / 900
  hx = 0.5 + math.cos(ang) * 0.3
  hy = 0.5 + math.sin(ang) * 0.3

  m = mat3().translate(cx - rad, cy - rad).scale(rad * 2, rad * 2)
  screen.pen = brush.gradient(brush.RADIAL, hx, hy, 1.0, 1.0, ORB, m)
  screen.shape(shape.circle(cx, cy, rad))
