import os
from badgeware import set_brightness
from easing import easeInOutCirc
import math


DEFAULT_ICON = image.load("default_icon.png")


class App:
    def __init__(self, collection, name, path, icon):
        self.index = len(collection)
        self.icon = icon
        self.name = name
        self.path = path
        collection.append(self)

    def draw(self, offset, scale=1, snap_x=False):
        # draw the icon sprite, scaled up for the supersampled framebuffer
        scale *= display.SCALE

        position = vec2(screen.width // 2, screen.height // 2)
        position += offset

        x = position.x - 12 * scale
        y = position.y - 12 * scale

        # A settled icon centres on a half physical pixel (screen.width // 2 is not
        # a multiple of the supersample factor), which smears it horizontally. Snap
        # the origin to the grid when it's at rest; the slide stays sub-pixel smooth.
        if snap_x:
            x = round(x / display.SCALE) * display.SCALE

        screen.blit(
            self.icon,
            rect(x, y, 24 * scale, 24 * scale)
        )


class Apps:
    def __init__(self, root):
        self.apps = []
        self.active_index = 0
        self.last_active = 0
        self.change_time = 0
        self.direction = -1
        self.launching = False

        def capitalize(word):
            if len(word) <= 1:
                return word
            return word[0].upper() + word[1:]

        for path in sorted(os.listdir(root)):
            name = " ".join([capitalize(word) for word in path.split("_")])

            if is_dir(f"{root}/{path}"):
                if path != "menu" and (file_exists(f"{root}/{path}/__init__.py") or file_exists(f"{root}/{path}/__init__.mpy")):
                    icon = image.load(f"{root}/{path}/icon.png") if file_exists(f"{root}/{path}/icon.png") else DEFAULT_ICON
                    App(self.apps, name, path, icon)

    @property
    def active(self):
        return self.apps[self.active_index]

    def prev(self):
        self.last_active = self.active_index
        self.active_index = (self.active_index - 1) % len(self)
        self.change_time = badge.ticks
        self.direction = -1

    def next(self):
        self.last_active = self.active_index
        self.active_index = (self.active_index + 1) % len(self)
        self.change_time = badge.ticks
        self.direction = 1

    def launch(self):
        self.change_time = badge.ticks
        self.launching = True

    def draw(self):
        app = self.apps[self.active_index]
        prev_app = self.apps[self.last_active]
        animation_done = False

        time_delta = badge.ticks - self.change_time

        if time_delta > 500:
            animation_done = True

        time_delta = min(time_delta, 500)
        time_delta = time_delta / 500

        scale = 1
        if self.launching:
            app.icon.alpha = int(255 * (1.0 - time_delta))
            scale += time_delta * 4
            time_delta = 1

        offset = vec2(screen.width, 0)
        offset *= easeInOutCirc(time_delta)
        offset *= self.direction

        prev_app.draw(offset)

        offset.x += -screen.width * self.direction
        if animation_done:
            offset.y += math.sin(badge.ticks / 150) * 2 * display.SCALE

        # snap the active icon to the grid once it's settled, so it sits crisp
        app.draw(offset, scale, snap_x=animation_done and not self.launching)

        if self.launching and animation_done:
            set_brightness(0.2)
            # hand the panel back to launched apps at native resolution
            badge.mode(LORES)
            return f"/system/apps/{app.path}"

        return None

    def __len__(self):
        return len(self.apps)

    def __getitem__(self, i):
        return self.apps[i]
