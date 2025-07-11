import time
from machine import Pin, I2C

# I2C setup
i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=10_000)
ADDR = 0x71

def write_display_ram(buf16: bytearray) -> None:
    """Send 16 bytes of display data to the LED matrix."""
    data = bytearray([0x00]) + buf16  # 0x00 is RAM address command
    i2c.writeto(ADDR, data)

# Initialization
time.sleep_ms(50)
try:
    i2c.writeto(ADDR, b'\x21')  # Turn on oscillator
    time.sleep_ms(2)
    i2c.writeto(ADDR, b'\x81')  # Display on, blink off
    time.sleep_ms(2)
    i2c.writeto(ADDR, b'\xEF')  # Max brightness

    # Display a "+" on the left and "o" on the right
    display_data: bytearray = bytearray([
        0x00,       # Row 0 (ignored/padding for RAM command)
        0x00, 0x00, # Row 1
        0x18, 0x18, # Row 2
        0x18, 0x24, # Row 3
        0x7E, 0x42, # Row 4
        0x7E, 0x42, # Row 5
        0x18, 0x24, # Row 6
        0x18, 0x18, # Row 7
        0x00, 0x00  # Row 8
    ])[1:]  # Skip the first padding byte for write_display_ram

    write_display_ram(display_data)
    print("Init OK!")
except OSError as e:
    print("Init failed:", e)
