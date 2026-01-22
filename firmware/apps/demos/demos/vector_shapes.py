import math


def update():
  screen.antialias = image.X4

  i = math.sin(io.ticks / 2000) * 0.2 + 0.5
  f = math.sin(io.ticks / 1000) * 150
  t = f + (math.sin(io.ticks / 500) + 1.0) * 50 + 100

  stroke = ((math.sin(io.ticks / 1000) + 1) * 0.05) + 0.1

  shapes = [
    shape.rectangle(-1, -1, 2, 2),
    shape.rectangle(-1, -1, 2, 2).stroke(stroke),
    shape.circle(0, 0, 1),
    shape.circle(0, 0, 1).stroke(stroke),
    shape.star(0, 0, 5, i, 1),
    shape.star(0, 0, 5, i, 1).stroke(stroke),
    shape.squircle(0, 0, 1),
    shape.squircle(0, 0, 1).stroke(stroke),
    shape.pie(0, 0, 1, f, t),
    shape.pie(0, 0, 1, f, t).stroke(stroke),
    shape.arc(0, 0, i, 1, f, t),
    shape.arc(0, 0, i, 1, f, t).stroke(stroke),
    shape.regular_polygon(0, 0, 1, 3),
    shape.regular_polygon(0, 0, 1, 3).stroke(stroke),
    shape.line(-0.75, -0.75, 0.75, 0.75, 0.5),
    shape.line(-0.75, -0.75, 0.75, 0.75, 0.5).stroke(stroke),
  ]
  
  shape_count = len(shapes)
  
  a = (io.ticks / 4000) % 1

  alpha_a = math.sin(a * math.pi / 2) * 255
  alpha_b = 255 - alpha_a
  
  offset = int((io.ticks / 4000) % shape_count)

  last_shape = shapes[(offset - 1) % len(shapes)]
  current_shape = shapes[offset]

  scale = ((math.sin(io.ticks / 2000 * math.pi) + 1) * 4) + 6
  transform = mat3().translate(screen.width / 2, screen.height / 2).rotate(io.ticks / 100).scale(scale)
  
  screen.pen = color.rgb(255, 255, 255, alpha_b * 0.5)
  last_shape.transform = transform
  screen.shape(last_shape)

  screen.pen = color.rgb(255, 255, 255, alpha_a * 0.5)
  current_shape.transform = transform
  screen.shape(current_shape)
