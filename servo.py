from machine import Pin, PWM
import time

class Servo:
    def __init__(self, pin, freq=50, min_us=500, max_us=2500):
        self.pwm = PWM(Pin(pin))
        self.pwm.freq(freq)
        self.min_us = min_us
        self.max_us = max_us
        self.freq = freq

    def angle_to_duty(self, angle):
        # Convert angle (0–180) to duty in microseconds
        us = self.min_us + (angle / 180) * (self.max_us - self.min_us)
        duty = int(us * 65535 * self.freq // 1000000)
        return duty

    def set_angle(self, angle):
        duty = self.angle_to_duty(angle)
        self.pwm.duty_u16(duty)

    def deinit(self):
        self.pwm.deinit()

if __name__ == '__main__':
    # Example usage:
    servo = Servo(pin=13)  # Use your actual GPIO pin
    servo.set_angle(0)    
    time.sleep(1)
    servo.set_angle(90)    
    #time.sleep(1)
    #servo.set_angle(180)   
    time.sleep(1)
    servo.deinit()

