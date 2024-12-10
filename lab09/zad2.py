#pip install adafruit-circuitpython-neopixel adafruit-circuitpython-bme280

import time
import board
import busio
import adafruit_bme280
import adafruit_ds18x20
import adafruit_onewire.bus
import neopixel

# Konfiguracja diod WS2812
pixel_pin = board.D18
num_pixels = 30
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.5, auto_write=False)

# Konfiguracja czujnika BME280
i2c = busio.I2C(board.SCL, board.SDA)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

# Konfiguracja czujnika DS18B20
ow_bus = adafruit_onewire.bus.OneWireBus(board.D4)
ds18b20 = adafruit_ds18x20.DS18X20(ow_bus.scan()[0])

def read_sensors():
    temperature = ds18b20.temperature
    humidity = bme280.humidity
    pressure = bme280.pressure
    return temperature, humidity, pressure

def visualize_data(temperature, humidity, pressure):
    # Przykładowa wizualizacja: zmiana koloru diod w zależności od temperatury
    for i in range(num_pixels):
        if temperature < 20:
            pixels[i] = (0, 0, 255)  # Niebieski
        elif 20 <= temperature < 25:
            pixels[i] = (0, 255, 0)  # Zielony
        else:
            pixels[i] = (255, 0, 0)  # Czerwony
    pixels.show()

def main():
    while True:
        temperature, humidity, pressure = read_sensors()
        print(f"Temperature: {temperature:.2f} C, Humidity: {humidity:.2f} %, Pressure: {pressure:.2f} hPa")
        visualize_data(temperature, humidity, pressure)
        time.sleep(1)

if __name__ == "__main__":
    main()
    
    
    
    
# pip install adafruit-circuitpython-neopixel adafruit-circuitpython-bme280 adafruit-circuitpython-encoder adafruit-circuitpython-mcp230xx
import time
import board
import busio
import adafruit_bme280
import adafruit_ds18x20
import adafruit_onewire.bus
import neopixel
import digitalio
from adafruit_mcp230xx.mcp23017 import MCP23017
from adafruit_seesaw import seesaw, rotaryio, digitalio as seesaw_digitalio

# Configuration for WS2812 LEDs
pixel_pin = board.D18
num_pixels = 30
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.5, auto_write=False)

# Configuration for BME280 sensor
i2c = busio.I2C(board.SCL, board.SDA)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

# Configuration for DS18B20 sensor
ow_bus = adafruit_onewire.bus.OneWireBus(board.D4)
ds18b20 = adafruit_ds18x20.DS18X20(ow_bus.scan()[0])

# Configuration for buttons and encoder
mcp = MCP23017(i2c)
button1 = mcp.get_pin(0)
button2 = mcp.get_pin(1)
button1.direction = digitalio.Direction.INPUT
button1.pull = digitalio.Pull.UP
button2.direction = digitalio.Direction.INPUT
button2.pull = digitalio.Pull.UP

seesaw = seesaw.Seesaw(i2c, addr=0x36)
encoder = rotaryio.IncrementalEncoder(seesaw)
last_position = None

def read_sensors():
    temperature = ds18b20.temperature
    humidity = bme280.humidity
    pressure = bme280.pressure
    return temperature, humidity, pressure

def visualize_data(temperature, humidity, pressure):
    for i in range(num_pixels):
        if temperature < 20:
            pixels[i] = (0, 0, 255)  # Blue
        elif 20 <= temperature < 25:
            pixels[i] = (0, 255, 0)  # Green
        else:
            pixels[i] = (255, 0, 0)  # Red
    pixels.show()

def main():
    global last_position
    while True:
        temperature, humidity, pressure = read_sensors()
        print(f"Temperature: {temperature:.2f} C, Humidity: {humidity:.2f} %, Pressure: {pressure:.2f} hPa")
        visualize_data(temperature, humidity, pressure)

        # Check button states
        if not button1.value:
            print("Button 1 pressed")
        if not button2.value:
            print("Button 2 pressed")

        # Check encoder position
        position = -encoder.position
        if position != last_position:
            print(f"Encoder position: {position}")
            last_position = position

        time.sleep(1)

if __name__ == "__main__":
    main()