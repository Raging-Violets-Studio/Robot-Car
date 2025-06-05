from machine import Pin, PWM
import time

PWM_FREQUENCY = 40  # Hz, common for all motors

# Mapping of motor channels: (pos_pin, neg_pin)
MOTOR_PINS = {
    'front_left':   (18, 19),  # M1
    'back_left':    (21, 20),  # M2
    'back_right':   (7,  6),   # M3
    'front_right':  (9,  8),   # M4
}

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
            self.pwm_pos.duty_u16(0)
            self.pwm_neg.duty_u16(0)

class MotorsController:
    """
    Controller managing all motors.
    """
    def __init__(self):
        self.motors = {
            name: Motor(name, *pins)
            for name, pins in MOTOR_PINS.items()
        }

    def set_all_motors_same_speed(self, speed):
        for motor in self.motors.values():
            motor.set_speed(speed)

    def test_motors(self, speed=20, duration=2):
        """Sequentially spin each motor to verify wiring."""
        for name, motor in self.motors.items():
            print(f"Testing {name} motor at speed {speed}")
            motor.set_speed(speed)
            time.sleep(duration)
            motor.set_speed(0)
            time.sleep(1)

if __name__ == '__main__':
    mc = MotorsController()
    mc.test_motors()
