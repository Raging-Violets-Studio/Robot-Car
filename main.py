import time
from motors import MotorsController
from battery_voltage_reader import BatteryVoltageReader  # assuming your class is in battery_voltage_reader.py

class Batmobile:
    """
    High-level controller for the 4WD Freenove car.
    """
    def __init__(self):
        self.motors_controller = MotorsController()
        self.battery_reader = BatteryVoltageReader()  # instantiate battery reader

    def move_straight(self, speed):
        """Drive all wheels at the same speed."""
        self.motors_controller.set_all_motors_same_speed(speed)

    def read_battery_voltage(self):
        """Return current battery voltage."""
        return self.battery_reader.read_battery_voltage()

    def start(self, target_speed, accel_time):
        """Smoothly ramp to target_speed over accel_time seconds."""
        print(f"Battery voltage before starting: {self.read_battery_voltage():.2f} V")
        sign = 1 if target_speed > 0 else -1
        abs_target = abs(target_speed)
        start = time.ticks_ms()
        current = 0
        print(f"Accelerating to {target_speed}")
        while abs(current) < abs_target:
            elapsed = time.ticks_ms() - start
            mag = int(min(abs_target, (elapsed / (accel_time*1000)) * abs_target))
            current = sign * mag
            self.move_straight(current)
            time.sleep(0.05)
        self.move_straight(target_speed)
        print("Reached target speed")
        print(f"Battery voltage after starting: {self.read_battery_voltage():.2f} V")

    def stop(self, current_speed, decel_time):
        """Smoothly ramp from current_speed to 0 over decel_time seconds."""
        print(f"Battery voltage before stopping: {self.read_battery_voltage():.2f} V")
        start = current_speed
        t0 = time.ticks_ms()
        current = current_speed
        print(f"Decelerating from {current_speed} to a stop.")
        while current != 0:
            elapsed = time.ticks_ms() - t0
            if start > 0:
                mag = max(0, start - (elapsed / (decel_time*1000))*start)
            else:
                mag = min(0, start + (elapsed / (decel_time*1000))*abs(start))
            current = int(mag)
            self.move_straight(current)
            time.sleep(0.05)
        self.move_straight(0)
        print("Stopped")
        print(f"Battery voltage after stopping: {self.read_battery_voltage():.2f} V")

if __name__ == '__main__':
    car = Batmobile()

    target_speed = 20
    accel_time = 5
    decel_time = 5

    car.start(target_speed=target_speed, accel_time=accel_time)
    time.sleep(5)
    car.stop(current_speed=target_speed, decel_time=decel_time)
