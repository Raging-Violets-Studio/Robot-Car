from machine import ADC, Pin

class BatteryVoltageReader:
    def __init__(self, adc_pin_num, vref=3.3, adc_resolution=1023, voltage_divider_ratio=4):
        """
        adc_pin_num: GPIO pin number connected to voltage divider output (ADC input)
        vref: reference voltage of ADC (usually 3.3V on Pico)
        adc_resolution: max ADC digital value (10-bit ADC -> 1023)
        voltage_divider_ratio: how much the voltage is scaled down (e.g. 4 means input voltage divided by 4)
        """
        self.adc = ADC(Pin(adc_pin_num))
        self.vref = vref
        self.adc_resolution = adc_resolution
        self.voltage_divider_ratio = voltage_divider_ratio

    def read_raw(self):
        """Read raw ADC value (0 to adc_resolution)"""
        return self.adc.read_u16() >> 6  # Convert 16-bit reading to 10-bit (shift right 6 bits)

    def read_voltage(self):
        """
        Convert raw ADC value to actual voltage at ADC pin.
        Formula: (raw / adc_resolution) * vref
        """
        raw = self.read_raw()
        voltage_at_pin = (raw / self.adc_resolution) * self.vref
        return voltage_at_pin

    def read_battery_voltage(self):
        """
        Calculate real battery voltage considering the voltage divider.
        Formula: voltage_at_pin * voltage_divider_ratio
        """
        voltage_at_pin = self.read_voltage()
        battery_voltage = voltage_at_pin * self.voltage_divider_ratio
        return battery_voltage

# Example usage
if __name__ == "__main__":
    battery_reader = BatteryVoltageReader(adc_pin_num=26)  # GPIO26 is ADC0 on Pico
    battery_volt = battery_reader.read_battery_voltage()
    print(f"Battery Voltage: {battery_volt:.2f} V")
