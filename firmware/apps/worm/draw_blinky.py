import sys
import os

sys.path.insert(0, "/system/apps/worm")
os.chdir("/system/apps/worm")

small_font = rom_font.nope
very_small_font = rom_font.sins

screen.antialias = image.X2

# Because of the strange shape of Blinky's screen bottom,
# we're just storing these as absolute values we can cycle through later.
score_locations = (
    vec2(13, 25),
    vec2(14, 25),
    vec2(15, 25),
    vec2(16, 25),
    vec2(13, 24),
    vec2(14, 24),
    vec2(15, 24),
    vec2(16, 24),
    vec2(13, 23),
    vec2(14, 23),
    vec2(15, 23),
    vec2(16, 23),
    vec2(13, 22),
    vec2(14, 22),
    vec2(15, 22),
    vec2(16, 22),
    vec2(22, 25),
    vec2(23, 25),
    vec2(24, 25),
    vec2(25, 25),
    vec2(22, 24),
    vec2(23, 24),
    vec2(24, 24),
    vec2(25, 24),
    vec2(22, 23),
    vec2(23, 23),
    vec2(24, 23),
    vec2(25, 23),
    vec2(22, 22),
    vec2(23, 22),
    vec2(24, 22),
    vec2(25, 22),
    vec2(7, 25),
    vec2(7, 24),
    vec2(6, 24),
    vec2(7, 23),
    vec2(6, 23),
    vec2(5, 23),
    vec2(7, 22),
    vec2(6, 22),
    vec2(5, 22),
    vec2(4, 22),
    vec2(3, 22),
    vec2(31, 25),
    vec2(31, 24),
    vec2(32, 24),
    vec2(31, 23),
    vec2(32, 23),
    vec2(33, 23),
    vec2(31, 22),
    vec2(32, 22),
    vec2(33, 22),
    vec2(34, 22),
    vec2(35, 22)
)


class renderer:
    def __init__(self):
        # Setting the basics of the grid.
        self.X_CELLS = 35
        self.Y_CELLS = 22
        self.CELL_SIZE = 1
        self.scroll = None
        self.scroll_window = image(screen.width, 10)

    # Drawing the intro is easy, we're just placing text and images.
    def draw_intro(self, game_speed):
        bg = image.load("assets/title.png")
        screen.blit(bg, vec2(0, 0))

        screen.pen = color.rgb(192, 192, 192)
        screen.line(vec2(12, 20), vec2(12 + (3 * game_speed) - 1, 20))
        screen.line(vec2(12, 21), vec2(12 + (3 * game_speed) - 1, 21))

    # Drawing the playfield isn't much harder.
    def draw_play(self, snake, apple, score):
        # Setting the screen to black, then making a rectangle for the actual playfield.
        screen.pen = color.rgb(0, 0, 0)
        screen.clear()

        screen.pen = color.rgb(192, 192, 192)

        screen.put(snake.x, snake.y)

        # Then we loop through the body, using get_orientation to pick a sprite and then draw it
        for i in range(len(snake.body)):
            segment = snake.body[i]
            if i % 2 == 0:
                screen.pen = color.rgb(128, 128, 128)
            else:
                screen.pen = color.rgb(96, 96, 96)

            screen.put(segment[0], segment[1])

        # Draw the apple.
        screen.pen = color.rgb(255, 255, 255)

        screen.put(apple.x, apple.y)

        if score > 0 and score < len(score_locations):
            for i in range(score):
                screen.put(score_locations[i])

    # Drawing the game over screen is again just images and text like the intro screen.
    def draw_gameover(self, score):
        if not self.scroll:
            self.scroll = scroll_text(f"Score: {score}", font_face=rom_font.ark, target=self.scroll_window)

        bg = image.load("assets/gameover.png")
        screen.blit(bg, vec2(0, 0))
        screen.pen = color.rgb(143, 143, 143)
        screen.blit(self.scroll_window, vec2(0, screen.height - 11))
        self.scroll()
