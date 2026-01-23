import os
from badgeware import is_dir, file_exists, set_brightness
import math


class App:
    def __init__(self, collection, name, path, icon):
        self.index = len(collection)
        self.icon = icon
        self.name = name
        self.path = path
        collection.append(self)

    def draw(self, offset, scale=1):
        # draw the icon sprite

        position = vec2(screen.width // 2, screen.height // 2)
        position += offset

        screen.blit(
            self.icon,
            rect(
                position.x - 12 * scale,
                position.y - 12 * scale,
                24 * scale,
                24 * scale
            )
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

        for path in os.listdir(root):
            name = " ".join([capitalize(word) for word in path.split("_")])

            if is_dir(f"{root}/{path}"):
                if file_exists(f"{root}/{path}/icon.png"):
                    App(self.apps, name, path, image.load(f"{root}/{path}/icon.png"))

    @property
    def active(self):
        return self.apps[self.active_index]

    def prev(self):
        self.last_active = self.active_index
        self.active_index = (self.active_index - 1) % len(self)
        self.change_time = io.ticks
        self.direction = -1

    def next(self):
        self.last_active = self.active_index
        self.active_index = (self.active_index + 1) % len(self)
        self.change_time = io.ticks
        self.direction = 1

    def launch(self):
        self.change_time = io.ticks
        self.launching = True

    def draw(self):
        app = self.apps[self.active_index]
        prev_app = self.apps[self.last_active]
        animation_done = False

        time_delta = io.ticks - self.change_time

        if time_delta > 250:
            animation_done = True

        time_delta = min(time_delta, 250)
        time_delta = time_delta / 250

        scale = 1
        if self.launching:
            set_brightness(0.2 - time_delta / 2)
            scale += time_delta * 4
            time_delta = 1

        offset = vec2(screen.width, 0)
        offset *= time_delta
        offset *= self.direction

        prev_app.draw(offset)

        offset.x += -screen.width * self.direction
        if animation_done:
            offset.y += math.sin(io.ticks / 150) * 2

        app.draw(offset, scale)

        if self.launching and animation_done:
            set_brightness(0.2)
            return f"/system/apps/{app.path}"

    def __len__(self):
        return len(self.apps)

    def __getitem__(self, i):
        return self.apps[i]
