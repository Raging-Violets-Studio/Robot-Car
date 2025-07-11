import time
from machine import Pin, I2C

class Eyes:
    def __init__(self, i2c, addr=0x71):
        self.i2c = i2c
        self.addr = addr
        self.init_driver()

    def init_driver(self):
        time.sleep_ms(50)
        self.i2c.writeto(self.addr, b'\x21')  # Oscillator ON
        time.sleep_ms(2)
        self.i2c.writeto(self.addr, b'\x81')  # Display ON, Blink OFF
        time.sleep_ms(2)
        self.i2c.writeto(self.addr, b'\xEF')  # Max brightness
        time.sleep_ms(2)

    def show(self, bitmap: bytearray):
        data = bytearray([0x00]) + bitmap
        self.i2c.writeto(self.addr, data)

    def instant_close(self):
        self.show(self.CLOSED)
        time.sleep(0.5)

    def wake_up_right_eye(self):
        frames = [
            self.LEFT_OPEN_RIGHT_CLOSED,
            self.LEFT_OPEN_RIGHT_THIN,
            self.LEFT_OPEN_RIGHT_PARTIAL,
            self.LEFT_OPEN_RIGHT_THIN,
            self.LEFT_OPEN_RIGHT_PARTIAL,
            self.OPEN
        ]
        delays = [0.6, 0.6, 0.6, 0.3, 0.3, 0.6]
        for frame, d in zip(frames, delays):
            self.show(frame)
            time.sleep(d)

    def right_wink(self, duration=0.4):
        """Close right eye briefly while left eye remains open."""
        self.show(self.LEFT_OPEN_RIGHT_CLOSED)
        time.sleep(duration)
        self.show(self.OPEN)

    # ────── Bitmaps ──────

    OPEN = bytearray([
        0x00, 0x00,
        0x18, 0x18,
        0x24, 0x24,
        0x5A, 0x5A,
        0x5A, 0x5A,
        0x24, 0x24,
        0x18, 0x18,
        0x00, 0x00
    ])

    CLOSED = bytearray([
        0x00, 0x00,
        0x08, 0x08,
        0x08, 0x08,
        0x08, 0x08,
        0x08, 0x08,
        0x08, 0x08,
        0x08, 0x08,
        0x00, 0x00
    ])

    LEFT_OPEN_RIGHT_CLOSED = bytearray([
        0x00, 0x00,
        0x18, 0x00,
        0x24, 0x00,
        0x5A, 0x08,
        0x5A, 0x08,
        0x24, 0x00,
        0x18, 0x00,
        0x00, 0x00
    ])

    LEFT_OPEN_RIGHT_THIN = bytearray([
        0x00, 0x00,
        0x18, 0x00,
        0x24, 0x00,
        0x5A, 0x10,
        0x5A, 0x10,
        0x24, 0x00,
        0x18, 0x00,
        0x00, 0x00
    ])

    LEFT_OPEN_RIGHT_PARTIAL = bytearray([
        0x00, 0x00,
        0x18, 0x10,
        0x24, 0x28,
        0x5A, 0x48,
        0x5A, 0x48,
        0x24, 0x28,
        0x18, 0x10,
        0x00, 0x00
    ])


# ───────────────────────────────
# Setup I2C for Pico W
# ───────────────────────────────
i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=100_000)
eyes = Eyes(i2c)

# ───────────────────────────────
# Wake-up Sequence + Right Wink
# ───────────────────────────────
print("Waking up slowly...")

eyes.show(eyes.OPEN)
time.sleep(2)

eyes.instant_close()
eyes.wake_up_right_eye()

# Now the right eye winks
eyes.right_wink()
print("Awake, and gave a right-eye wink!")
