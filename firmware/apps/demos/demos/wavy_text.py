import math

canvas = image(screen.width, screen.height)
update_text = None

def update():
    global update_text

    update_text = update_text or scroll_text(f" Hello World ", target=canvas, continuous=True, speed=screen.width)

    update_text()

    for x in range(screen.width):
        canvas.alpha = int(math.sin(x / screen.width * math.pi) * 128)
        y = math.sin(io.ticks / 100 + (x / screen.width * math.pi)) * 4
        screen.blit(canvas, rect(x, 0, 1, screen.height), rect(x, y, 1, screen.height))
        
    canvas.alpha = 255
