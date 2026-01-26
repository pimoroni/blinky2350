import os
import network
from machine import Pin, Timer, ADC
import time
import powman
import gc
from badgeware import rtc, display, set_brightness

"""

Hardware Error Codes:

E1 - Wireless scan fail - unable to detect networks.
E2 - Charging Fail
E3 - RTC Alarm was in a triggered state in pre checks.
E4 - RTC Alarm didn't trigger after timer
E5 - VBUS DETECT Fail or timed out
E6 - VBUS Detect was in a triggered state in pre checks.
E7 - VBAT SENSE reading was out of range
E8 - SW_POWER_EN function test failed
E10 - MAC Address invalid
E11 - Time out during button test
E17 - Failed to start CYW43 (RM2 Module)
E18 - PSRAM Test Failure

"""

set_brightness(0.1)

WIDTH, HEIGHT = screen.width, screen.height

CL = [Pin(0, Pin.OUT), Pin(1, Pin.OUT),
      Pin(2, Pin.OUT), Pin(3, Pin.OUT)]

charge_stat = Pin.board.CHARGE_STAT
vbus_detect = Pin.board.VBUS_DETECT
sw_int = Pin.board.BUTTON_INT
rtc_alarm = Pin.board.RTC_ALARM
vbat = ADC(Pin.board.VBAT_SENSE)

up = Pin.board.BUTTON_UP
down = Pin.board.BUTTON_DOWN
a = Pin.board.BUTTON_A
b = Pin.board.BUTTON_B
c = Pin.board.BUTTON_C
home = Pin.board.BUTTON_HOME
power = Pin.board.POWER_EN

font_ignore = rom_font.smart
screen.font = font_ignore


class Tests:
    def __init__(self):

        self.wifi_pass = None
        self.buttons_pass = False
        self.vbus_pass = False
        self.rtc_pass = None

        sw_int.irq(self.btn_handler)

        # RTC Setup
        self.rtc = rtc
        self.rtc.clear_timer_flag()
        self.rtc.enable_timer_interrupt(True)
        self.rtc_start = time.time()

        # Toggle the case lights once every second
        self.cl_timer = Timer()
        self.cl_timer.init(mode=Timer.PERIODIC, period=1000, callback=self.cl_toggle)

        # We want to check the RTC alarm has trigger
        self.rtc_timer = Timer()

        # Raspberry Pi Vendor ID
        self.vendor = "28:CD:C1"

        # a dict to store the button name, state and label location on screen
        self.buttons = {"A": [False, (7, 21)], "B": [False, (16, 21)],
                        "C": [False, (25, 21)], "UP": [False, (WIDTH - 5, 3)],
                        "DOWN": [False, (WIDTH - 5, 12)], "HOME": [False, (16, 1)]}

    def test_wireless(self):

        self.wlan = network.WLAN(network.WLAN.IF_STA)
        self.wlan.active(True)
        self.mac = self.wlan.config("mac")

        try:
            if self.wifi_pass is None:
                data = ":".join([f"{b:02X}" for b in self.mac])
                print(self.wlan.config("mac"))
                results = self.wlan.scan()

                if len(results) == 0:
                    raise Exception("E1")

                if data[:8] != self.vendor:
                    raise Exception("E10")

                self.wifi_pass = True
        except OSError:
            raise Exception("E17") from None

    def display_error(self, error):
        screen.pen = color.black
        screen.clear()
        screen.pen = color.white
        screen.text(str(error), 5, 3)
        display.update()

    def test_buttons(self):
        # Check if all buttons have been pressed
        if not self.buttons_pass:
            for button in self.buttons:
                if not self.buttons[button][0]:
                    return

            self.buttons_pass = True
            print("BUTTONS: OK!")

    def test_charge_stat(self):
        # if battery charging is not detected
        # raise an exception and end the test
        print(charge_stat.value())
        if charge_stat.value() == 1:
            raise Exception("E2")

    def test_psram(self):
        ram_free = round(gc.mem_free() / 1000000, 1)

        if ram_free < 8.2 or not powman._test_psram_cs():  # noqa: SLF001
            raise Exception("E18")

    def clear(self):
        screen.pen = color.black
        screen.clear()
        screen.pen = color.white

    def test_display(self):

        self.clear()

        # Left to right
        for x in range(WIDTH):
            screen.rectangle(x, 0, 1, HEIGHT)
            display.update()
            time.sleep(0.03)

        time.sleep(1)
        self.clear()

        # Top to bottom
        for y in range(HEIGHT):
            screen.rectangle(0, y, WIDTH, 1)
            display.update()
            time.sleep(0.03)

        time.sleep(1)

    def test_vbat(self):
        voltage = vbat.read_u16() * (3.3 / 65536) * 2
        if voltage >= 4.2 or voltage < 3.6:
            raise Exception("E7")

    # Toggle the case lights on the back of the badge
    def cl_toggle(self, _t):
        for led in CL:
            led.toggle()
        time.sleep(0.2)

    def clear_flag(self):
        # Now the test has complete, we can remove the flag.
        try:
            os.remove("state/hardware_test.txt")
        except OSError:
            pass

    # Handle the user exiting the test
    # This is only enabled once the function tests have passed
    def exit_handler(self, _pin):
        # The test has passed so we can clear the flag.
        self.clear_flag()

        # Time to sleep now!
        powman.sleep()

    def run(self):

        try:

            self.test_charge_stat()

            # We want to check we can toggle the SW_POWER_EN pin.
            # We're going to do it here before the rest of test starts
            power.off()
            if power.value():
                # Not that you'd see this error with no LED power xD
                raise Exception("E8")

            power.on()
            if not power.value():
                raise Exception("E8")

            self.test_psram()

            # Set the timers for the RTC test
            self.rtc.set_timer(2)
            self.rtc_timer.init(mode=Timer.ONE_SHOT, period=2100, callback=self.test_rtc)

            # If the pin for RTC alarm is already low, there's a problem.
            if rtc_alarm.value() == 0:
                raise Exception("E3")

            # If the pin for VBUS DETECT is already low, there's a problem.
            if vbus_detect.value() == 0:
                raise Exception("E6")

            self.test_wireless()

            if not self.vbus_pass:
                self.test_vbus()

            if self.rtc_pass is False:
                raise Exception("E4")

            button_timeout = time.time()
            while True:
                if time.time() - button_timeout > 10:
                    raise Exception("E11")

                self.test_buttons()

                # Home button can't interrupt so we check it here.
                if not int(home.value()):
                    self.buttons["HOME"][0] = True

                if self.buttons_pass:
                    break

                self.draw()

        except Exception as e:   # noqa BLE001
            print(e)
            while True:
                self.display_error(e)

        b.irq(self.exit_handler)
        self.cl_timer.deinit()
        self.display_error("OK")
        time.sleep(0.2)
        while True:
            self.test_display()

    # Interrupt based button testing checks the button gpio
    # and that each button is able to trigger sw_int
    def btn_handler(self, _pin):
        if not int(a.value()):
            self.buttons["A"][0] = True

        if not int(b.value()):
            self.buttons["B"][0] = True

        if not int(c.value()):
            self.buttons["C"][0] = True

        if not int(up.value()):
            self.buttons["UP"][0] = True

        if not int(down.value()):
            self.buttons["DOWN"][0] = True

    def test_rtc(self, _t):
        # By the time this handler is used
        # the RTC alarm should have triggered
        self.rtc_pass = not rtc_alarm.value()
        self.rtc_timer.deinit()

    def test_vbus(self):
        start_time = time.time()

        while True:
            self.display_error("<")
            # Time out to catch the user not removing the USB
            # Or to end the test if there's a failure on VBUS_DETECT
            if time.time() - start_time < 5:
                # We're checking status of the USB connection here.
                # If it changes we're going to assume the user removed it.
                if vbus_detect.value() == 0:
                    self.test_vbat()
                    self.vbus_pass = True
                    # little sleep here so we can read the charge status
                    time.sleep(0.2)
                    break
            else:
                raise Exception("E5")

    def draw(self):
        # Clear screen and display title
        screen.pen = color.black
        screen.clear()
        screen.pen = color.white

        # Draw button presses
        for button in sorted(self.buttons):
            pressed = self.buttons[button][0]
            if not pressed:
                x, y = self.buttons[button][1]
                screen.shape(shape.rectangle(x, y, 7, 7))
        display.update()


t = Tests()

t.run()
