import machine

"""
This test should fire the irq every 2s
"""

def irq(pin):
    print(pin.value())

machine.Pin.board.RTC_ALARM.irq(irq)

machine.I2C().writeto_mem(0x51, 0x00, bytes([0b00000000])) # Reset Control_1 to default values
machine.I2C().writeto_mem(0x51, 0x01, bytes([0b00000000])) # Clear interrupt flag
machine.I2C().writeto_mem(0x51, 0x10, bytes([0b00000010])) # Set timer to 2s
machine.I2C().writeto_mem(0x51, 0x11, bytes([0b00010111])) # Interrupt enable + timer enable + mode seconds

while True:
    pass
