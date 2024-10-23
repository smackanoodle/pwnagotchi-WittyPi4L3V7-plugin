import logging
import time
import struct
import RPi.GPIO as GPIO

from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts
import pwnagotchi.plugins as plugins
import pwnagotchi


class UPS:
    def __init__(self):
        # only import when the module is loaded and enabled
        import smbus2 as smbus
        # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)
        self._bus = smbus.SMBus(1)
        self._is_pro = False
        self.voltage_history = []  # List to store voltage readings
        self.max_history_size = 40  # Maximum number of readings to keep
        GPIO.setmode(GPIO.BCM)  # Set the GPIO mode to BCM
        GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Configure GPIO-4 as input with pull-up resistor
        GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP)


    def voltage(self):
        try:
            address = 0x08  # WittyPi4L3V7 address
            # Pull input voltage from i2c
            input_voltage_integer = self._bus.read_byte_data(address, 1)
            input_voltage_decimal = self._bus.read_byte_data(address, 2)
            input_voltage = input_voltage_integer + (input_voltage_decimal / 100.0) 
            
            # Update voltage history
            if len(self.voltage_history) >= self.max_history_size:
                self.voltage_history.pop(0)
            self.voltage_history.append(input_voltage)
            
            # Calculate the average voltage
            avg_voltage = sum(self.voltage_history) / len(self.voltage_history) if self.voltage_history else 0.0
            return avg_voltage
        except:
            return 0.0

    def rstVhist(self):
        self.voltage_history = []

    def capacity(self):
        battery_curve = [
            [4.20, 4.16, 100, 100],
            [4.05, 4.16, 87.5, 100],
            [4.00, 4.05, 75, 87.5],
            [3.92, 4.00, 62.5, 75],
            [3.86, 3.92, 50, 62.5],
            [3.79, 3.86, 37.5, 50],
            [3.66, 3.79, 25, 37.5],
            [3.52, 3.66, 12.5, 25],
            [3.49, 3.52, 6.2, 12.5],
            [3.0, 3.49, 0, 6.2],    
            [0, 3.0, 0, 0],         
        ]
        battery_level = 0
        battery_v = self.voltage()
        for range in battery_curve:
            if range[0] < battery_v <= range[1]:
                level_base = ((battery_v - range[0]) / (range[1] - range[0])) * (range[3] - range[2])
                battery_level = level_base + range[2]
        return round(battery_level, 0)

    def USBin(self):
        # Pull bit from power mode register
        PowerMode = self._bus.read_byte_data(0x08, 7)
        return PowerMode

    def shutdwn(self):
        # Check for shutdown from button GPIO
        try:
            pin_state = GPIO.input(4)
            return pin_state
        except:
            return GPIO.HIGH

    def full(self):
        try:
            charge_state = GPIO.input(6)
            return charge_state
        except:
            return GPIO.HIGH

    def died(self):
        oop = self._bus.read_byte_data(0x08, 8)
        return oop

class WittyPi4L3V7(plugins.Plugin):
    __author__ = 'cookieninja667288@gmail.com'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'A plugin that will add a voltage indicator for the Witty Pi 4 L3V7'

    def __init__(self):
        self.ups = None

    def on_loaded(self):
        self.ups = UPS()
        logging.info("[WittyPi4L3V7] plugin loaded.")

    def on_ui_setup(self, ui):
        ui.add_element("bat", LabeledValue(color=BLACK, label='BAT', value='0%', position=(ui.width() / 2 + 15, 0), label_font=fonts.Bold, text_font=fonts.Medium))
        if self.ups.died() == 1:
            ui.update(force=True, new_data={'status': 'Finally ... Some POWER!!'})
            time.sleep(3)


    def on_unload(self, ui):
        with ui._lock:
            ui.remove_element("bat")

    def on_ui_update(self, ui):
        if self.ups.USBin() == 0:  # If USB is plugged in
            if self.ups.full() == GPIO.LOW:
                ui.set("bat", "$$ %")
                self.ups.rstVhist()
            else:
                ui.set("bat", "^^ %")
            if self.ups.shutdwn() == GPIO.LOW:
                ui.update(force=True, new_data={'status': 'Witty shut me off, bye ...'})
                time.sleep(3)
                pwnagotchi.shutdown()
        else:
            capacity = int(self.ups.capacity())
            ui.set("bat", str(capacity) + "%")
            if self.ups.shutdwn() == GPIO.LOW:
                ui.update(force=True, new_data={'status': 'Witty shut me off, bye ...'})
                time.sleep(3)
                pwnagotchi.shutdown()
