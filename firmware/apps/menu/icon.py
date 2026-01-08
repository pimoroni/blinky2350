
# bright icon colours
bold = [
    color.rgb(211, 250, 55),
    color.rgb(48, 148, 255),
    color.rgb(95, 237, 131),
    color.rgb(225, 46, 251),
    color.rgb(216, 189, 14),
    color.rgb(255, 128, 210),
]

# create faded out variants for inactive icons
fade = 1.8
faded = [
    color.rgb(211 / fade, 250 / fade, 55 / fade),
    color.rgb(48 / fade, 148 / fade, 255 / fade),
    color.rgb(95 / fade, 237 / fade, 131 / fade),
    color.rgb(225 / fade, 46 / fade, 251 / fade),
    color.rgb(216 / fade, 189 / fade, 14 / fade),
    color.rgb(255 / fade, 128 / fade, 210 / fade),
]

# icon shape
squircle = shape.squircle(0, 0, 5, 2)
shade_brush = color.rgb(0, 0, 0, 30)


class Icon:
    active_icon = None

    def __init__(self, pos, name, index, icon):
        self.active = False
        self.pos = pos
        self.icon = icon
        self.name = name
        self.index = index
        self.spin = False

    def activate(self, active):
        # if this icon wasn't already activated then flag it for the spin animation
        if not self.active and active:
            self.spin = True
            self.spin_start = io.ticks
        self.active = active
        if active:
            Icon.active_icon = self

    def draw(self):
        width = 1
        sprite_width = self.icon.width
        sprite_offset = sprite_width / 2

#         if self.spin:
#             # create a spin animation that runs over 100ms
#             speed = 300
#             frame = io.ticks - self.spin_start
#
#             # calculate the width of the tile during this part of the animation
#             width = round(math.cos(frame / speed) * 3) / 3
#
#             # ensure the width never reduces to zero or the icon disappears
#             width = max(0.1, width) if width > 0 else min(-0.1, width)
#
#             # determine how to offset and scale the sprite to match the tile width
#             sprite_width = width * self.icon.width
#             sprite_offset = abs(sprite_width) / 2
#
#             # once the animation has completed unset the spin flag
#             if frame > (speed * 6):
#                 self.spin = False

        # draw the icon sprite
        if sprite_width > 0:
            self.icon.alpha = 255 if self.active else 100
            screen.blit(
                self.icon,
                point(self.pos[0] - sprite_offset - 1,
                      self.pos[1] - 13)
            )
