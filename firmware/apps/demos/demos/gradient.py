import math

ORB = [
  (0.0, color.rgb(255, 255, 255)),
  (0.35, color.rgb(120, 210, 255)),
  (1.0, color.rgb(18, 28, 84)),
]

W, H = screen.width, screen.height
CX, CY = W * 0.5, H * 0.5
RAD = min(W, H) * 0.55

# map the 0..1 square onto the circle's bounding box
ORB_M = mat3().translate(CX - RAD, CY - RAD).scale(RAD * 2, RAD * 2)

# Built once. What construction costs is the 256-entry lookup table, and that
# depends only on the stops, so the rolling highlight is repositioned with
# geometry() each frame instead of rebuilding the brush.
orb_brush = brush.gradient(brush.RADIAL, 0.5, 0.5, 1.0, 1.0, ORB, ORB_M)


def update():
  screen.antialias = image.X4

  # roll the highlight around so the orb reads like a rotating lit sphere
  ang = badge.ticks / 900
  hx = 0.5 + math.cos(ang) * 0.3
  hy = 0.5 + math.sin(ang) * 0.3

  orb_brush.geometry(hx, hy, 1.0, 1.0, ORB_M)
  screen.pen = orb_brush
  screen.shape(shape.circle(CX, CY, RAD))
