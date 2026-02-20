# Your app's directory
APP_DIR = "/system/apps/clock"

import sys
import os

# Standalone bootstrap for finding app assets
os.chdir(APP_DIR)

# Standalone bootstrap for module imports
sys.path.insert(0, APP_DIR)

from badgeware import State
import time
import ntptime
from daylightsaving import DaylightSavingPolicy, DaylightSaving
from machine import RTC
import math
import wifi
import secrets
from fallingsand import FallingSand

# Enable a 1s timer
rtc.set_timer(1)

SCREEN_MAIN_W = screen.width - 4
SCREEN_MAIN_H = screen.height - 4


# making classes for which clock is displayed etc, so we can refer to them by name
class DisplayType:
    textclock = 1
    sandclock = 2
    sevenseg = 3
    scribble = 4


class ClockState:
    Running = 0
    ConnectWiFi = 2
    UpdateTime = 3


secrets.require("REGION", "TIMEZONE")

REGION = secrets.REGION
TIMEZONE = secrets.TIMEZONE


# setting up default values for the first run, and loading in the state with the
# user choices if the file's there.
state = {
    "clock_style": 4
}

State.load("clock", state)

clock_state = ClockState.Running

# Loading all the assets.
textclock_font = rom_font.winds
dots_font = rom_font.hungry
small_font = rom_font.torch

faded_brush = color.rgb(255, 255, 255, 100)
bg_brush = color.rgb(0, 0, 0)
drawing_brush = color.rgb(255, 255, 255)

falling_sand = FallingSand()

if state["clock_style"] == DisplayType.scribble:
    numerals = SpriteSheet("assets/scribble_num.png", 10, 1)
    background = image.load("assets/scribble_bg.png")
    clock_dots = image.load("assets/scribble_dots.png")
elif state["clock_style"] == DisplayType.sevenseg:
    numerals = SpriteSheet("assets/sevenseg_num.png", 10, 1)
    clock_dots = SpriteSheet("assets/sevenseg_dots.png", 2, 1)
    background = None
    foreground = None

month_days = {
    1: 31,
    2: 28,
    3: 31,
    4: 30,
    5: 31,
    6: 30,
    7: 31,
    8: 31,
    9: 30,
    10: 31,
    11: 30,
    12: 31
}

calendar_months = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec"
}

# These are the different Daylight Saving time zones, according to the Wikipedia article.
# Timezones are incredibly complex, we've covered the main ones here.
# "zonename": (hemisphere, week, month, weekday, hour, timezone, minutes clocks change by)
# Israel and Palestine each follow different daylight saving rules from standard, and are not included here.
regions = {
    "us": (0, 2, 3, 6, 2, 1, 11, 6, 2, 60),
    "cuba": (0, 2, 3, 6, 0, 1, 11, 6, 1, 60),
    "eu": (0, 0, 3, 6, 1, 0, 10, 6, 1, 60),
    "moldova": (0, 0, 3, 6, 2, 0, 10, 6, 3, 60),
    "lebanon": (0, 0, 3, 6, 0, 0, 10, 6, 0, 60),
    "egypt": (0, 0, 4, 4, 0, 0, 10, 3, 24, 60),
    "chile": (1, 1, 9, 5, 24, 1, 4, 5, 24, 60),
    "australia": (1, 1, 10, 6, 2, 1, 4, 6, 3, 60),
    "nz": (1, 0, 9, 6, 2, 1, 4, 6, 3, 60)
}


def user_message(caption, line1):
    # A simple message screen with a single line of text.

    small_font = rom_font.winds

    screen.pen = color.black
    screen.clear()
    screen.font = small_font
    screen.pen = color.white
    screen.text(caption, vec2(0, 1))

    screen.font = small_font
    screen.text(line1, vec2(0, 9))


def center_point(text, img):
    # Return the x-coordinate of some text if you want it centred on the screen.

    w, h = img.measure_text(text)
    return (img.width / 2) - (w / 2)


def update_time(region, timezone):
    # Set the time with ntptime and pass it to the daylight saving calculator.
    # Pass the result to the unit's RTC.

    # handle time out during ntp comms
    try:
        ntptime.settime()
        time.sleep(2)
    except OSError:
        return False

    timezone_minutes = timezone * 60

    hemisphere, week_in, month_in, weekday_in, hour_in, week_out, month_out, weekday_out, hour_out, mins_difference = regions[region]

    dstp = DaylightSavingPolicy(hemisphere, week_in, month_in, weekday_in, hour_in, timezone_minutes + mins_difference)
    stdp = DaylightSavingPolicy(hemisphere, week_out, month_out, weekday_out, hour_out, timezone_minutes)

    dst = DaylightSaving(dstp, stdp)
    t = time.mktime(time.gmtime())
    tm = time.gmtime(dst.localtime(t))
    RTC().datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))
    year, month, day, dow, hour, minute, second, dow = RTC().datetime()
    rtc.datetime((year, month, day, hour, minute, second, dow))

    return True


def display_time():
    # Chooses which clock face to show based on the state["clock_style"] global.

    global clock_dots, numerals, background, foreground

    currenttime = rtc.datetime()

    if state["clock_style"] == DisplayType.textclock:
        draw_text_clock(currenttime)

    elif state["clock_style"] == DisplayType.sandclock:
        # Here we're seeing if the timer's gone off from one second ago,
        # and if it has we're checking if we need to drop any grains and
        # resetting the RTC timer for one second's time.
        if rtc.timer_elapsed():
            falling_sand.assess_drop(currenttime)
            rtc.set_timer(1)
        falling_sand.drop_grains()
        draw_sand_clock(currenttime)

    elif state["clock_style"] == DisplayType.scribble:
        numerals = SpriteSheet("assets/scribble_num.png", 10, 1)
        background = image.load("assets/scribble_bg.png")
        clock_dots = image.load("assets/scribble_dots.png")
        draw_scribble_clock(currenttime)

    elif state["clock_style"] == DisplayType.sevenseg:
        numerals = SpriteSheet("assets/sevenseg_num.png", 10, 1)
        clock_dots = SpriteSheet("assets/sevenseg_dots.png", 2, 1)
        background = None
        foreground = None
        draw_sevenseg_clock(currenttime)


def draw_scribble_clock(currenttime):
    # Scribble is simple,
    # all the hard work is done by the images.

    this_drawing_brush = color.rgb(0, 0, 0)
    screen.clear()

    # First draw the background
    screen.blit(background, vec2(0, 0))

    # Draw the digits just like in the 7 segment clock...
    hour = currenttime[3]
    minute = currenttime[4]

    digit_h = numerals.sprite(0, 0).height

    screen.pen = this_drawing_brush
    digit_y = math.floor((SCREEN_MAIN_H - digit_h) / 2)

    # Simply divide the hours and minutes into individual digits...
    hourtens = math.floor(hour / 10)
    hourunits = hour % 10
    minutetens = math.floor(minute / 10)
    minuteunits = minute % 10

    # ...and then use that to pick a sprite from the spritesheet of numerals.
    screen.blit(numerals.sprite(hourtens, 0), vec2(0, digit_y))
    screen.blit(numerals.sprite(hourunits, 0), vec2(9, digit_y))
    screen.blit(numerals.sprite(minutetens, 0), vec2(18, digit_y))
    screen.blit(numerals.sprite(minuteunits, 0), vec2(27, digit_y))


def draw_sevenseg_clock(currenttime):
    # The seven segment display is very similar to the scribble one.

    screen.pen = bg_brush
    screen.clear()
    screen.pen = drawing_brush

    # Draw the digits just like in the 7 segment clock...
    hour = currenttime[3]
    minute = currenttime[4]

    digit_h = numerals.sprite(0, 0).height

    digit_y = math.floor((SCREEN_MAIN_H - digit_h) / 2) - 2

    # Simply divide the hours and minutes into individual digits...
    hourtens = math.floor(hour / 10)
    hourunits = hour % 10
    minutetens = math.floor(minute / 10)
    minuteunits = minute % 10

    # ...and then use that to pick a sprite from the spritesheet of numerals.
    screen.blit(numerals.sprite(hourtens, 0), vec2(0, digit_y))
    screen.blit(numerals.sprite(hourunits, 0), vec2(8, digit_y))
    screen.blit(numerals.sprite(minutetens, 0), vec2(19, digit_y))
    screen.blit(numerals.sprite(minuteunits, 0), vec2(27, digit_y))

    # Then make up a string for the date and draw it.
    month = calendar_months[currenttime[1]]
    mday = currenttime[2]

    date = str(mday) + " " + month

    screen.font = small_font
    screen.text(date, vec2(0, 13))

    screen.antialias = image.X4
    screen.shape(shape.rectangle(0, 1, currenttime[5] / 60 * 39, 1))

    # Quickly draw the dots in between the numerals, flashing every second
    if currenttime[5] % 2:
        screen.blit(clock_dots.sprite(0, 0), vec2(16, digit_y))
    else:
        screen.blit(clock_dots.sprite(1, 0), vec2(16, digit_y))


def draw_sand_clock(currenttime):
    # First we'll clear the screen

    screen.pen = bg_brush
    screen.clear()

    # Let's advance the sand simulation one step, then draw it.
    falling_sand.simulate_sand()
    falling_sand.draw_sand(screen)

    # Now we're just turning the time into a pretty string.
    # We have to use this method to do the leading zeroes
    # as unlike Python, Micropython doesn't have zfill()
    screen.font = textclock_font
    screen.pen = drawing_brush

    hour = str(currenttime[3])
    hour = ("0" * (2 - len(hour))) + hour
    minute = str(currenttime[4])
    minute = ("0" * (2 - len(minute))) + minute
    second = str(currenttime[5])
    second = ("0" * (2 - len(second))) + second

    time_text = hour + ":" + minute + ":" + second
    screen.text(time_text, vec2(0, 12))

    # Finally just drawing a line between the text and the sand.
    screen.shape(shape.rectangle(0, 12, 39, 1))


def draw_text_clock(currenttime):
    # The text clock, just as in the other models, only involves writing text to the screen.

    screen.pen = bg_brush
    screen.clear()

    # We've got three rows of text here, they all start out blank.
    # We'll be using the other variables to work it out, as in
    # certain cases the lines need to be swapped around.
    top_row = ""
    middle_row = ""
    bottom_row = ""

    fraction = ""
    descriptor = ""
    hour = ""

    # We need to work out which number on a clock face we're
    # currently closest to.
    hours = currenttime[3]
    minutes_in_seconds = (currenttime[4] * 60) + currenttime[5]
    hour_portion = (minutes_in_seconds + 150) / 300
    minutes = math.floor(hour_portion)

    # Depending on that, we just do a bunch of checks to decide which words
    # to put into which variables.
    if minutes == 0 or minutes == 12:
        fraction = "o'clock"
    if minutes == 1 or minutes == 11:
        fraction = "five"
    if minutes == 5 or minutes == 7:
        fraction = "25"
    if minutes == 2 or minutes == 10:
        fraction = "ten"
    if minutes == 3 or minutes == 9:
        fraction = "quarter"
    if minutes == 4 or minutes == 8:
        fraction = "twenty"
    if minutes == 6:
        fraction = "half"

    if minutes <= 6 and minutes > 0:
        descriptor = "past"
    elif minutes == 12:
        hours += 1
    elif minutes > 6 and minutes < 12:
        descriptor = " to"
        hours += 1
    if hours > 23:
        hours -= 24

    if hours == 0 or hours == 12:
        hour = "twelve"
    if hours == 1 or hours == 13:
        hour = "one"
    if hours == 2 or hours == 14:
        hour = "two"
    if hours == 3 or hours == 15:
        hour = "three"
    if hours == 4 or hours == 16:
        hour = "four"
    if hours == 5 or hours == 17:
        hour = "five"
    if hours == 6 or hours == 18:
        hour = "six"
    if hours == 7 or hours == 19:
        hour = "seven"
    if hours == 8 or hours == 20:
        hour = "eight"
    if hours == 9 or hours == 21:
        hour = "nine"
    if hours == 10 or hours == 22:
        hour = "ten"
    if hours == 11 or hours == 23:
        hour = "eleven"

    # Put the different variables into different rows
    # depending on the order they need to be shown in.
    if fraction == "o'clock":
        top_row = hour
        middle_row = fraction
    else:
        top_row = fraction
        middle_row = descriptor
        bottom_row = hour

    # Finally write these lines of text into a new image and
    # blit that to the screen. We do this rather than writing to the screen
    # so that we're not trying to write text starting outside the screen area.
    readout = image(39, 26)

    readout.pen = drawing_brush
    readout.font = textclock_font

    readout.text(top_row, center_point(top_row, readout), 0)
    readout.text(middle_row, center_point(middle_row, readout), 7)
    readout.text(bottom_row, center_point(bottom_row, readout), 14)

    screen.blit(readout, vec2(0, -3))


def write_settings():
    # Simply saves the chosen style of clock as a state.
    State.save("clock", state)


def update():
    # Main update loop.

    global state, clock_state

    wifi.tick()

    # First we check if anything's been pressed before choosing what to display.
    if badge.pressed(BUTTON_C):
        state["clock_style"] += 1
        if state["clock_style"] > 4:
            state["clock_style"] = 1
        write_settings()

    if badge.pressed(BUTTON_A):
        state["clock_style"] -= 1
        if state["clock_style"] < 1:
            state["clock_style"] = 4
        write_settings()

    # If the year in the RTC is 2021 or earlier, we need to sync so it has the same effect as pressing B.
    if badge.pressed(BUTTON_B) or time.gmtime()[0] <= 2021 and clock_state == ClockState.Running:
        user_message("updating", "time")
        clock_state = ClockState.ConnectWiFi

    # So here we just decide what to do based on the clock_state global.
    # Running is normal operation, but if B was detected as pressed above,
    # then we go through states to get the WiFi details, connect and finally
    # pull the time from the NTP server.

    # We use states here because the screen doesn't update until the end of Update(),
    # so anything we put on the display will be overwritten by anything we put further down.
    # By using states each step of the process happens on a different loop through Update(),
    # so we can display a message for each step.
    if clock_state == ClockState.Running:
        display_time()

    elif clock_state == ClockState.UpdateTime:
        if update_time(REGION, TIMEZONE):
            clock_state = ClockState.Running
        else:
            user_message("Unable", "to get time.")

    elif clock_state == ClockState.ConnectWiFi:
        user_message("Please", "Wait...")
        if wifi.connect():
            clock_state = ClockState.UpdateTime


run(update)
