
# Your apps directory
APP_DIR = "/system/apps/tomato"

import os
import sys

# Standalone bootstrap for finding app assets
os.chdir(APP_DIR)

# Standalone bootstrap for module imports
sys.path.insert(0, APP_DIR)

import time

from badgeware import run, set_brightness

# Centre points for the display
CX = screen.width // 2
CY = screen.height // 2

small_font = pixel_font.load("/system/assets/fonts/winds.ppf")
large_font = pixel_font.load("/system/assets/fonts/smart.ppf")
screen.font = small_font

scroll = None
scroll_window = image(screen.width, 10)


def center_text(text, y):
    global scroll

    w, _ = screen.measure_text(text)

    # if the text is too long to be centered on the display, we'll start scrolling text
    if w <= screen.width:
        screen.text(text, screen.width / 2 - (w / 2), y)
    else:
        if not scroll:
            scroll = text.scroll(text, font_face=rom_font.winds, target=scroll_window, bg=color.black)
        else:
            scroll()
            screen.blit(scroll_window, vec2(0, CY - 1))

class Tomato(object):
    def __init__(self):

        self.background = color.black
        self.foreground = color.white  # Slightly lighter for foreground elements.

        # Time constants.
        # Feel free to change these to ones that work better for you.
        self.TASK = 25 * 60
        self.SHORT = 10 * 60
        self.LONG = 30 * 60

        # How long the completion alert should be played (seconds)
        self.alert_duration = 5
        self.alert_start_time = 0
        self.last_toggle = 0

        self.is_break_time = False
        self.start_time = 0
        self.tasks_complete = 0
        self.running = False
        self.paused = False
        self.time_elapsed = 0
        self.current_timer = self.TASK

        self.btn_pos = ((CX - 8), screen.height - 18)

    def draw(self):

        # Clear the screen
        screen.pen = color.black
        screen.clear()

        # unpack the button position
        x, y = self.btn_pos

        # Draw the button text, the text shown here depends on the current timer state
        screen.pen = self.foreground
        screen.font = small_font
        if not self.running:
            if self.is_break_time:
                center_text("Start Break", y + 3)
            else:
                center_text("Start Task", y + 3)
        elif self.running and self.paused:
            center_text("Resume", y + 3)
        else:
            center_text("Pause", y + 3)

        text = self.return_string()
        screen.font = large_font
        if self.is_break_time:
            screen.pen = color.white
            screen.rectangle(0, 0, screen.width, 13)
            screen.pen = color.black
        center_text(text, -2)
        screen.rectangle(CX - 3, screen.height - 5, 7, 7)

    def run(self):

        self.alert_start_time = 0

        if self.is_break_time:
            self.background = color.white
            if self.tasks_complete < 4:
                self.current_timer = self.SHORT
            else:
                self.current_timer = self.LONG
        else:
            self.current_timer = self.TASK
            self.background = color.black

        if not self.running:
            self.reset()
            self.running = True
            self.start_time = time.time()
        elif self.running and not self.paused:
            self.paused = True
        elif self.running and self.paused:
            self.paused = False
            self.start_time = time.time() - self.time_elapsed

    def reset(self):
        self.start_time = 0
        self.time_elapsed = 0

    def case_lights_off(self):
        badge.set_caselights(0)

    def toggle_case_lights(self):
        if badge.ticks - self.last_toggle > 250:
            lights = [1.0 - light for light in badge.get_caselights()]
            badge.set_caselights(*lights)
            self.last_toggle = badge.ticks

    def update(self):

        if time.time() - self.alert_start_time < self.alert_duration:
            self.toggle_case_lights()
        else:
            self.case_lights_off()

        if self.running and not self.paused:

            # Dim the backlight when the timer is running
            set_brightness(0.05)

            self.time_elapsed = time.time() - self.start_time

            if self.time_elapsed >= self.current_timer:
                self.running = False
                self.alert_start_time = time.time()
                if not self.is_break_time:
                    if self.tasks_complete < 4:
                        self.tasks_complete += 1
                    else:
                        self.tasks_complete = 0
                self.is_break_time = not self.is_break_time
        else:
            # restore the backlight to default brightness
            set_brightness(0.3)

    # Return the remaining time formatted in a string for displaying with vector text.
    def return_string(self):
        minutes, seconds = divmod(self.current_timer - self.time_elapsed, 60)
        return f"{minutes:02d}:{seconds:02d}"


# Create an instance of our timer object
def init():
    global timer
    timer = Tomato()


def on_exit():
    pass


def update():
    global timer, scroll

    if badge.pressed(BUTTON_B):
        scroll = None
        timer.run()
    timer.draw()
    timer.update()


# Standalone support for Thonny debugging
if __name__ == "__main__":
    run(update, init=init, on_exit=on_exit)
