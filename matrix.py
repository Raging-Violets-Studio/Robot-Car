import time
from machine import I2C

# ─────────────────────────────────────────────────────────────
# Base LED Matrix Driver
# ─────────────────────────────────────────────────────────────
class LEDMatrix:
    def __init__(self, i2c: I2C, addr: int = 0x71):
        self.i2c = i2c
        self.addr = addr
        self._init_driver()

    def _init_driver(self):
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


# ─────────────────────────────────────────────────────────────
# Eye Expressions
# ─────────────────────────────────────────────────────────────
class Eyes(LEDMatrix):
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
        self.show(self.LEFT_OPEN_RIGHT_CLOSED)
        time.sleep(duration)
        self.show(self.OPEN)

    def glance(self, eye="left", direction="center"):
        """
        Moves the 2x2 pupil in the given eye to the specified direction.
        Direction: 'center', 'left', 'right', 'up', 'down'
        """
        base = self.OPEN[:]

        pupil_positions = {
            "center": (3, 3),
            "left":   (3, 2),
            "right":  (3, 4),
            "up":     (2, 3),
            "down":   (4, 3)
        }

        if direction not in pupil_positions:
            print("Invalid glance direction:", direction)
            return

        def modify_pupil(x, y, action):
            """Clear or draw the 2x2 pupil at (x, y)."""
            for dy in range(2):
                row = y + dy
                if row < 0 or row >= 8:
                    continue
                for dx in range(2):
                    col = x + dx
                    bit = 1 << (7 - col)
                    index = row * 2 if eye == "left" else row * 2 + 1
                    if action == "clear":
                        base[index] &= ~bit
                    elif action == "draw":
                        base[index] |= bit

        # Step 1: Clear the default center pupil
        modify_pupil(3, 3, "clear")

        # Step 2: Draw the new pupil at the desired location
        x, y = pupil_positions[direction]
        modify_pupil(x, y, "draw")

        self.show(base)


    def test_eyes(self):
        self.show(self.OPEN)
        time.sleep(1)

        directions = ["center", "left", "right", "up", "down"]
        for d in directions:
            self.glance("left", d)
            time.sleep(0.6)

        for d in directions:
            self.glance("right", d)
            time.sleep(0.6)

        self.show(self.OPEN)
        time.sleep(1)

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


# ─────────────────────────────────────────────────────────────
# Symbol Display Utility
# ─────────────────────────────────────────────────────────────
class Symbols(LEDMatrix):
    SYMBOLS = {
        "plus": [
            0x18,
            0x18,
            0x7E,
            0x7E,
            0x18,
            0x18,
            0x00,
            0x00
        ],
        "circle": [
            0x18,
            0x24,
            0x42,
            0x42,
            0x42,
            0x24,
            0x18,
            0x00
        ],
        "x": [
            0x81,
            0x42,
            0x24,
            0x18,
            0x18,
            0x24,
            0x42,
            0x81
        ],
        "none": [0x00] * 8
    }

    def display(self, left: str = "none", right: str = "none"):
        """
        Display symbols on left and right halves of the matrix.
        """
        left_data = self.SYMBOLS.get(left, self.SYMBOLS["none"])
        right_data = self.SYMBOLS.get(right, self.SYMBOLS["none"])

        bitmap = bytearray(16)
        for row in range(8):
            bitmap[row * 2] = left_data[row]
            bitmap[row * 2 + 1] = right_data[row]

        self.show(bitmap)

    def test_symbol_display(self):
        print("Running Symbol Display Test...")
        self.display(left="plus", right="circle")
        time.sleep(2)
        self.display(left="x", right="plus")
        time.sleep(2)
        self.display()
        print("Symbol Display Test Complete.")


# ───────────────────────────────
# Demo Usage
# ───────────────────────────────
if __name__ == "__main__":
    from machine import Pin, I2C

    print("Starting matrix.py demo")

    i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=100_000)

    eyes = Eyes(i2c)
    symbols = Symbols(i2c)

    # Uncomment the test you'd like to run:
    eyes.test_eyes()
    # symbols.test_symbol_display()

    print("Demo complete.")
