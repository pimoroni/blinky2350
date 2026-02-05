import math

def update():
  x = screen.width // 2
  y = screen.height // 2
  custom_pattern = brush.pattern(color.rgb(255, 255, 255, 200), color.rgb(0, 0, 0, 0), (
    0b00000000,
    0b01111110,
    0b01000010,
    0b01011010,
    0b01011010,
    0b01000010,
    0b01111110,
    0b00000000))
  screen.pen = custom_pattern
  screen.shape(shape.circle(x + math.cos(badge.ticks / 500) * 10, y + math.sin(badge.ticks / 1000) * 10, 10))

  built_in_pattern = brush.pattern(color.rgb(255, 255, 255, 100), color.rgb(0, 0, 0, 0), 11)
  screen.pen = built_in_pattern
  screen.shape(shape.circle(x + math.sin(badge.ticks / 250) * 20, y + math.cos(badge.ticks / 500) * 20, 10))

  built_in_pattern = brush.pattern(color.rgb(255, 255, 255, 50), color.rgb(0, 0, 0, 0), 8)
  screen.pen = built_in_pattern
  screen.shape(shape.circle(x + math.cos(badge.ticks / 250) * 10, y + math.sin(badge.ticks / 500) * 10, 10))
