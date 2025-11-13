import gc
import json
import os
import io as stream
import sys
import time
import pcf85063a

import machine
import powman
import blinky
from picovector import brushes, shapes, screen, PixelFont, io, Image, Matrix  # noqa F401


ASSETS = "/system/assets"
WIDTH, HEIGHT = screen.width, screen.height
DEFAULT_FONT = PixelFont.load(f"{ASSETS}/fonts/sins.ppf")
ERROR_FONT = PixelFont.load(f"{ASSETS}/fonts/desert.ppf")

SLEEP_TIMEOUT_MS = 30 * 1000

# RTC
rtc = pcf85063a.PCF85063A(machine.I2C())
display = blinky.Blinky()
screen.font = DEFAULT_FONT


class Colors:
    GREEN_1 = brushes.color(86, 211, 100)
    GREEN_2 = brushes.color(46, 160, 67)
    GREEN_3 = brushes.color(25, 108, 46)
    GREEN_4 = brushes.color(3, 58, 22)
    GRAY_1 = brushes.color(242, 245, 243)
    GRAY_2 = brushes.color(228, 235, 230)
    GRAY_3 = brushes.color(182, 191, 184)
    GRAY_4 = brushes.color(144, 150, 146)
    GRAY_5 = brushes.color(35, 41, 37)
    GRAY_6 = brushes.color(16, 20, 17)

    BLACK = brushes.color(0, 0, 0)
    WHITE = brushes.color(255, 255, 255)

    RED = brushes.color(255, 0, 0)
    YELLOW = brushes.color(255, 255, 0)
    GREEN = brushes.color(0, 255, 0)
    TEAL = brushes.color(0, 255, 255)
    BLUE = brushes.color(0, 0, 255)
    PURPLE = brushes.color(255, 0, 255)


def localtime_to_rtc():
    rtc.datetime(time.localtime())


def rtc_to_localtime():
    dt = rtc.datetime()
    machine.RTC().datetime((dt[0], dt[1], dt[2], dt[6], dt[3], dt[4], dt[5], 0))


def time_from_ntp():
    import ntptime

    ntptime.settime()
    del sys.modules["ntptime"]
    gc.collect()
    localtime_to_rtc()


if time.localtime()[0] >= 2025:
    localtime_to_rtc()

elif rtc.datetime()[0] >= 2025:
    rtc_to_localtime()


# We can rely on these having been set up by powman... maybe
BUTTON_DOWN = machine.Pin.board.BUTTON_DOWN
BUTTON_A = machine.Pin.board.BUTTON_A
BUTTON_B = machine.Pin.board.BUTTON_B
BUTTON_C = machine.Pin.board.BUTTON_C
BUTTON_UP = machine.Pin.board.BUTTON_UP
BUTTON_HOME = machine.Pin.board.BUTTON_HOME

VBAT_SENSE = machine.ADC(machine.Pin.board.VBAT_SENSE)
VBUS_DETECT = machine.Pin.board.VBUS_DETECT
CHARGE_STAT = machine.Pin.board.CHARGE_STAT
SENSE_1V1 = machine.ADC(machine.Pin.board.SENSE_1V1)

SYSTEM_VERY_SLOW = 0
SYSTEM_SLOW = 1
SYSTEM_NORMAL = 2
SYSTEM_FAST = 3
SYSTEM_TURBO = 4

BAT_MAX = 4.10
BAT_MIN = 3.00

BUTTONS = {BUTTON_DOWN, BUTTON_A, BUTTON_B, BUTTON_C, BUTTON_UP}

conversion_factor = 3.3 / 65536


# takes a text string (that may include newline characters) and performs word
# wrapping. returns a line of lines and their widths as a result.
def wrap_and_measure(image, text, size, max_width):
    result = []
    for line in text.splitlines():
        # if max_width is specified then perform word wrapping
        if max_width:
            # setup a start and end cursor to traverse the text
            start, end = 0, 0
            last_width = 0
            i = 0
            while True:
                i += 1
                # search for the next space
                end = line.find(" ", end)
                if end == -1:
                    end = len(line)

                # measure the text up to the space
                width, _ = image.measure_text(line[start:end], size)
                if width >= max_width:
                    # line exceeded max length
                    new_end = line.rfind(" ", start, end)
                    if new_end == -1:
                        result.append((line[start:end], last_width))
                        start = end + 1
                    else:
                        result.append((line[start:new_end], last_width))
                        start = new_end + 1
                elif end == len(line):
                    # reached the end of the string
                    result.append((line[start:end], width))
                    break

                # step past the last space
                end += 1
                last_width = width
        else:
            # no wrapping needed, just return the original line with its width
            width, _ = image.measure_text(line, size)
            result.append((line, width))

    return result


def clamp(v, vmin, vmax):
    return max(vmin, min(v, vmax))


def file_exists(path):
    try:
        os.stat(path)
        return True
    except OSError:
        return False


def is_dir(path):
    try:
        flags = os.stat(path)
        return flags[0] & 0x4000  # is a directory
    except:  # noqa: E722
        return False


class SpriteSheet:
    def __init__(self, file, columns, rows):
        self.image = Image.load(file)
        self.sw = int(self.image.width / columns)
        self.sh = int(self.image.height / rows)

        self.sprites = []
        for x in range(columns):
            column = []
            for y in range(rows):
                sprite = self.image.window(self.sw * x, self.sh * y, self.sw, self.sh)
                column.append(sprite)
            self.sprites.append(column)

    def sprite(self, x, y):
        return self.sprites[x][y]

    def animation(self, x=0, y=0, count=None, horizontal=True):
        if not count:
            count = int(self.image.width / self.sw)
        return AnimatedSprite(self, x, y, count, horizontal)


class AnimatedSprite:
    def __init__(self, spritesheet, x, y, count, horizontal=True):
        self.spritesheet = spritesheet
        self.frames = []
        for _ in range(count):
            self.frames.append((x, y))
            if horizontal:
                x += 1
            else:
                y += 1

    def frame(self, frame_index=0):
        frame_index = int(frame_index)
        frame_index %= len(self.frames)
        return self.spritesheet.sprite(
            self.frames[frame_index][0], self.frames[frame_index][1]
        )

    def count(self):
        return len(self.frames)


class BitmapFont:
    def __init__(self, file, char_width, char_height):
        self.image = Image.load(file)
        self.cw = char_width
        self.ch = char_height

        columns = self.image.width / self.cw
        rows = self.image.height / self.ch

        self.chars = []
        for y in range(rows):
            for x in range(columns):
                self.chars.append(
                    self.image.window(self.cw * x, self.ch * y, self.cw, self.ch)
                )

    def text(self, image, x, y, text, max_width=None, only_measure=False):
        cx, cy = 0, 0  # caret pos
        maxx, maxy = 0, 0

        lines = text.splitlines()
        for line in lines:
            words = line.split(" ")
            for word in words:
                # work out length of word in pixels
                wl = len(word) * self.cw

                # move to next line if exceeds max width
                if max_width and cx + wl > max_width:
                    cx = 0
                    cy += self.ch - 2

                # render characters in word
                for char in word:
                    char_idx = ord(char)
                    if not only_measure and char_idx < len(self.chars):
                        image.blit(self.chars[char_idx], cx + x, cy + y)
                    cx += self.cw

                    if max_width and cx > max_width:
                        cx = 0
                        cy += self.ch - 2

                # once the word has been rendered update our min and max cursor values
                maxx = max(maxx, cx)
                maxy = max(maxy, cy + self.ch - 2)

                cx += self.cw / 3

            cx = 0
            cy += self.ch - 2

        return maxx, maxy

    def measure(self, text, max_width=None):
        return self.text(None, 0, 0, text, max_width=max_width, only_measure=True)


class Particle:
    def __init__(self, position, motion, user=None):
        self.position = position
        self.motion = motion
        self.user = user
        self.created_at = time.ticks_ms()

    def age(self):
        return (time.ticks_ms() - self.created_at) / 1000


class ParticleGenerator:
    def __init__(self, gravity, max_age=2):
        self.gravity = gravity
        self.max_age = max_age
        self.last_tick_ms = time.ticks_ms()
        self.particles = []

    def spawn(self, position, motion, user=None):
        self.particles.append(Particle(position, motion, user))

    def youngest(self):
        return self.particles[-1] if len(self.particles) > 0 else None

    # update all particle locations and age out particles that have expired
    def tick(self):
        # expire aged particles
        self.particles = [
            particle for particle in self.particles if particle.age() < self.max_age
        ]

        # update particles
        dt = (time.ticks_ms() - self.last_tick_ms) / 1000
        for particle in self.particles:
            particle.position = (
                particle.position[0] + (particle.motion[0] * dt),
                particle.position[1] + (particle.motion[1] * dt),
            )

            # apply "gravity" force to motion vectors
            particle.motion = (
                (particle.motion[0] + self.gravity[0] * dt),
                (particle.motion[1] + self.gravity[1] * dt),
            )

        self.last_tick_ms = time.ticks_ms()


# show the current free memory including the delta since last time the
# function was called, optionally include a custom message
_lf = None


def free(message=""):
    global _lf
    import gc

    gc.collect()  # collect any free memory before reporting
    f = int(gc.mem_free() / 1024)
    print(f"{message}: {f}kb", end="")
    if _lf:
        delta = f - _lf
        sign = "-" if delta < 0 else "+"
        print(f" ({sign}{abs(delta)}kb)", end="")
    print("")
    _lf = f


def woken_by_button():
    return powman.get_wake_reason() in (
        powman.WAKE_BUTTON_A,
        powman.WAKE_BUTTON_B,
        powman.WAKE_BUTTON_C,
        powman.WAKE_BUTTON_UP,
        powman.WAKE_BUTTON_DOWN,
    )


def pressed_to_wake(button):
    # TODO: BUTTON_HOME cannot be a wake button
    # so maybe raise an exception
    return button in powman.get_wake_buttons()


def woken_by_reset():
    return powman.get_wake_reason() == 255


def sleep():
    #display.set_backlight(0)
    powman.sleep()


class Assets:
    @staticmethod
    def font(name):
        file = f"{ASSETS}/fonts/{name}.ppf"
        try:
            return PixelFont.load(file)
        except OSError as e:
            raise ValueError(f'Font "{name}" not found. (Missing {file}?)') from e

    @staticmethod
    def fonts():
        return [f[:-4] for f in os.listdir(f"{ASSETS}/fonts") if f.endswith(".ppf")]


def is_charging():
    # We only want to return the charge status if the USB cable is connected.
    if VBUS_DETECT.value():
        return not CHARGE_STAT.value()

    return False


def get_usb_connected():
    return bool(VBUS_DETECT.value())


def sample_adc_u16(adc, samples=1):
    val = []
    for _ in range(samples):
        val.append(adc.read_u16())
    return sum(val) / len(val)


def get_battery_level():
    # Use the battery voltage to estimate the remaining percentage

    # Get the average reading over 20 samples from our VBAT and VREF
    voltage = sample_adc_u16(VBAT_SENSE, 10) * conversion_factor * 2
    vref = sample_adc_u16(SENSE_1V1, 10) * conversion_factor
    voltage = voltage / vref * 1.1

    # Return the battery level as a percentage
    return min(100, max(0, round(123 - (123 / pow((1 + pow((voltage / 3.2), 80)), 0.165)))))


def get_battery_level():
    # Use the battery voltage to estimate the remaining percentage

    # Get the average reading over 20 samples from our VBAT and VREF
    voltage = sample_adc_u16(VBAT_SENSE, 10) * conversion_factor * 2
    vref = sample_adc_u16(SENSE_1V1, 10) * conversion_factor
    voltage = voltage / vref * 1.1

    # Return the battery level as a percentage
    return min(100, max(0, round(123 - (123 / pow((1 + pow((voltage / 3.2), 80)), 0.165)))))


def get_disk_usage(mountpoint="/"):
    # f_bfree and f_bavail should be the same?
    # f_files, f_ffree, f_favail and f_flag are unsupported.
    f_bsize, f_frsize, f_blocks, f_bfree, _, _, _, _, _, f_namemax = os.statvfs(
        mountpoint
    )

    f_total_size = f_frsize * f_blocks
    f_total_free = f_bsize * f_bfree
    f_total_used = f_total_size - f_total_free

    f_used = 100 / f_total_size * f_total_used
    f_free = 100 / f_total_size * f_total_free

    return f_total_size, f_used, f_free


class State:
    @staticmethod
    def delete(app):
        try:
            os.remove("/state/{}.json".format(app))
        except OSError:
            pass

    @staticmethod
    def save(app, data):
        try:
            with open("/state/{}.json".format(app), "w") as f:
                f.write(json.dumps(data))
                f.flush()
        except OSError:
            import os

            try:
                os.stat("/state")
            except OSError:
                os.mkdir("/state")
                State.save(app, data)

    @staticmethod
    def modify(app, data):
        state = {}
        State.load(app, state)
        state.update(data)
        State.save(app, state)

    @staticmethod
    def load(app, defaults):
        try:
            data = json.loads(open("/state/{}.json".format(app), "r").read())
            if type(data) is dict:
                defaults.update(data)
                return True
        except (OSError, ValueError):
            pass

        State.save(app, defaults)
        return False


def run(update, init=None, on_exit=None):
    try:
        if init:
            init()
        try:
            while True:
                io.poll()
                if (result := update()) is not None:
                    return result
                gc.collect()
                display.update()
        except KeyboardInterrupt:
            pass
        finally:
            if on_exit:
                on_exit()

    except Exception as e:  # noqa: BLE001
        warning("Error!", get_exception(e))



def get_exception(e):
    s = stream.StringIO()
    sys.print_exception(e, s)
    s.seek(0)
    s.readline()  # Drop the "Traceback" bit
    return s.read()


# Draw an overlay box with a given message within it
def message(title, text, window=None):
    error_window = window or screen.window(0, 0, screen.width, screen.height)
    error_window.font = DEFAULT_FONT

    # Draw a light grey background
    background = shapes.rounded_rectangle(
        0, 0, error_window.width, error_window.height, 5, 5, 5, 5
    )
    heading = shapes.rounded_rectangle(0, 0, error_window.width, 12, 5, 5, 0, 0)
    error_window.brush = brushes.color(100, 100, 100, 200)
    error_window.draw(background)

    error_window.brush = brushes.color(255, 100, 100, 200)
    error_window.draw(heading)

    error_window.brush = brushes.color(50, 100, 50)
    tw = 35
    error_window.draw(
        shapes.rounded_rectangle(
            error_window.width - tw - 10, error_window.height - 12, tw, 12, 3, 3, 0, 0
        )
    )

    error_window.brush = brushes.color(255, 200, 200)
    error_window.text(
        "Okay", error_window.width - tw + 5 - 10, error_window.height - 12
    )
    y = 0
    error_window.text(title, 5, y)
    y += 17

    error_window.brush = brushes.color(200, 200, 200)
    text_lines = wrap_and_measure(error_window, text, 12, error_window.width - 10)
    for line, _width in text_lines:
        error_window.text(line, 5, y)
        y += 10

    display.update()
    while True:
        io.poll()
        if io.pressed:
            break
    while io.pressed:
        io.poll()


def warning(title, text):
    print(f"- ERROR: {text}")
    message(title, text)


if __name__ == "__main__":
    warning("Hello from badgeware.py", "Why are you running me?")
