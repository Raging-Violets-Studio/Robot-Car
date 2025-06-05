from machine import ADC, Pin

class BatteryVoltageReader:
    def __init__(self, adc_pin_num=26, vref=3.3, adc_resolution=4095, voltage_divider_ratio=4):
        """
        adc_pin_num: GPIO pin number connected to voltage divider output (ADC input)
        vref: reference voltage of ADC (usually 3.3V on Pico)
        adc_resolution: max ADC digital value (12-bit ADC -> 4095)
        voltage_divider_ratio: ratio of voltage divider, e.g. 4 means input voltage divided by 4
        """
        self.adc = ADC(Pin(adc_pin_num))
        self.vref = vref
        self.adc_resolution = adc_resolution
        self.voltage_divider_ratio = voltage_divider_ratio

    def read_battery_voltage(self):
        """
        Read and return the estimated battery voltage.

        MicroPython's ADC.read_u16() returns a 16-bit value (0–65535), but the Raspberry Pi Pico's ADC
        is actually 12-bit (2^12 = 4096 levels). This means only the upper 12 bits are meaningful,
        and the lower 4 bits are padding.

        To convert the 16-bit value to its actual 12-bit equivalent:
        - Think of the 16-bit number as: [12 meaningful bits][4 insignificant bits]
        - We discard the 4 least significant bits using a right shift (`>> 4`)
        or integer division by 16 (`// 16`)
        - This yields a scaled value from 0 to 4095 — a proper 12-bit range

        After converting to 12-bit:
        - The voltage at the ADC pin is computed based on the reference voltage and resolution
        - Then we multiply by the voltage divider ratio to get the estimated battery voltage

        Returns:
            float: Estimated battery voltage in volts.
        """
        raw_adc = self.adc.read_u16()       # 16-bit value (0–65535)
        scaled_adc = raw_adc >> 4           # Convert to 12-bit scale (0–4095)

        voltage_at_adc = (scaled_adc / self.adc_resolution) * self.vref
        battery_voltage = voltage_at_adc * self.voltage_divider_ratio

        return battery_voltage



if __name__ == '__main__':
    battery_reader = BatteryVoltageReader()
    battery_volt = battery_reader.read_battery_voltage()
    print(f"Battery Voltage: {battery_volt:.2f} V")
