# freenove_car.py
# Refactored motor control using OOP and clear separation of concerns

from machine import Pin, PWM
import time

# ===== Configuration =====
PWM_FREQUENCY = 40  # Hz, common for all motors

# Mapping of motor channels: (pos_pin, neg_pin)
MOTOR_PINS = {
    'front_left':   (18, 19),  # M1
    'back_left':    (21, 20),  # M2
    'back_right':   (7,  6),   # M3
    'front_right':  (9,  8),   # M4
}

# ===== Motor Class =====
class Motor:
    """
    Represents a single bidirectional motor controlled by two PWM inputs.
    """
    def __init__(self, name, pos_pin, neg_pin, freq=PWM_FREQUENCY):
        self.name = name
        self.pwm_pos = PWM(Pin(pos_pin))
        self.pwm_neg = PWM(Pin(neg_pin))
        self.pwm_pos.freq(freq)
        self.pwm_neg.freq(freq)

    def set_speed(self, speed):
        """
        Set motor speed: -100..100. Positive = forward, negative = backward.
        """
        duty = int((abs(speed) / 100) * 65535)
        if speed > 0:
            self.pwm_pos.duty_u16(duty)
            self.pwm_neg.duty_u16(0)
        elif speed < 0:
            self.pwm_pos.duty_u16(0)
            self.pwm_neg.duty_u16(duty)
        else:
            # stop
            self.pwm_pos.duty_u16(0)
            self.pwm_neg.duty_u16(0)

# ===== Car Controller =====
class FreenoveCar:
    """
    High-level controller for the 4WD Freenove car.
    """
    def __init__(self):
        # Instantiate motors
        self.motors = {
            name: Motor(name, *pins)
            for name, pins in MOTOR_PINS.items()
        }

    def move_straight(self, speed):
        """Drive all wheels at the same speed."""
        for m in self.motors.values():
            m.set_speed(speed)

    def start(self, target_speed, accel_time):
        """Smoothly ramp to target_speed over accel_time seconds."""
        sign = 1 if target_speed > 0 else -1
        abs_target = abs(target_speed)
        start = time.ticks_ms()
        current = 0
        while abs(current) < abs_target:
            elapsed = time.ticks_ms() - start
            mag = int(min(abs_target, (elapsed / (accel_time*1000)) * abs_target))
            current = sign * mag
            print(f"[{current}]")
            self.move_straight(current)
            time.sleep_ms(50)
        self.move_straight(target_speed)
        print("Reached target speed")

    def stop(self, current_speed, decel_time):
        """Smoothly ramp from current_speed to 0 over decel_time seconds."""
        start = current_speed
        t0 = time.ticks_ms()
        current = current_speed
        while current != 0:
            elapsed = time.ticks_ms() - t0
            if start > 0:
                mag = max(0, start - (elapsed / (decel_time*1000))*start)
            else:
                mag = min(0, start + (elapsed / (decel_time*1000))*abs(start))
            current = int(mag)
            print(f"[{current}]")
            self.move_straight(current)
            time.sleep_ms(50)
        self.move_straight(0)
        print("Stopped")

    def test_motors(self, speed=50, duration=2):
        """Sequentially spin each motor to verify wiring."""
        for name, m in self.motors.items():
            print(f"Testing {name}")
            m.set_speed(speed)
            time.sleep(duration)
            m.set_speed(0)
            time.sleep(1)

# ===== Main Sequence =====
if __name__ == '__main__':
    car = FreenoveCar()

    # Example drive
    target_speed=20
    accel_time=5
    decel_time=5
    
    car.start(target_speed=target_speed, accel_time=accel_time)
    time.sleep(5)
    
    car.stop(current_speed=target_speed, decel_time=decel_time)

