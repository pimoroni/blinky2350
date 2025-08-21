import machine

from pcf85063a import PCF85063A


"""
This test should fire a single interrupt event,
it seems to print out 1 and then 0 (the irq firing)
"""

def irq(pin):
    print(pin.value())


machine.Pin.board.RTC_ALARM.irq(irq)


rtc = PCF85063A(machine.I2C())
rtc.clear_alarm_flag()
rtc.enable_alarm_interrupt(True)
rtc.enable_timer_interrupt(False)

rtc.datetime((2025, 5, 30, 8, 7, 12, 1))
rtc.set_alarm(15, 7, 8)

while True:
    pass
