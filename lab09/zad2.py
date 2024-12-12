#pip install adafruit-circuitpython-neopixel adafruit-circuitpython-bme280
import time
import os
import board
import neopixel
import RPi.GPIO as GPIO
import w1thermsensor
import busio
import adafruit_bme280.advanced as adafruit_bme280
from config import *

# WS2812 config
LED_COUNT = 8
LED_PIN = board.D18
LED_BRIGHTNESS = 1.0 / 32
pixels = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness=LED_BRIGHTNESS, auto_write=False)

# ds18b20
def ds18b20():
    sensor = w1thermsensor.W1ThermSensor()
    temp = sensor.get_temperature()
    return temp

# bme280
def bme280():
    i2c = busio.I2C(board.SCL, board.SDA)
    bme = adafruit_bme280.Adafruit_BME280_I2C(i2c, 0x76)

    bme.sea_level_pressure = 1013.25
    bme.standby_period = adafruit_bme280.STANDBY_TC_500
    bme.iir_filter = adafruit_bme280.IIR_FILTER_X16
    bme.overscan_pressure = adafruit_bme280.OVERSCAN_X16
    bme.overscan_humidity = adafruit_bme280.OVERSCAN_X1
    bme.overscan_temperature = adafruit_bme280.OVERSCAN_X2

    return bme

# visualize temparature on WS2812
def visualize_temperature(temp):
    temp_color = (0, 0, 255) if temp < 20 else (255, 255, 0) if temp < 30 else (255, 0, 0)
    intensity = min(max(int(temp / 5), 1), LED_COUNT)
    for i in range(LED_COUNT):
        pixels[i] = temp_color if i < intensity else (0, 0, 0)
    pixels.show()

# visualize humidity on WS2812
def visualize_humidity(humidity):
    humidity_color = (0, 255, 0)
    intensity = min(max(int(humidity / 20), 1), LED_COUNT)
    for i in range(LED_COUNT):
        pixels[i] = humidity_color if i < intensity else (0, 0, 0)
    pixels.show()

# visualize pressure on WS2812
def visualize_pressure(pressure):
    pressure_color = (0, 255, 255)
    intensity = min(max(int((pressure - 900) / 50), 1), LED_COUNT)
    for i in range(LED_COUNT):
        pixels[i] = pressure_color if i < intensity else (0, 0, 0)
    pixels.show()

# button handler
def button_pressed_callback(channel):
    global current_mode
    if channel == buttonRed:
        current_mode = (current_mode - 1) % 3
    elif channel == buttonGreen:
        current_mode = (current_mode + 1) % 3

# encoder handler
def read_encoder():
    global current_mode
    left_state = GPIO.input(encoderLeft)
    right_state = GPIO.input(encoderRight)

    if left_state == GPIO.LOW:
        time.sleep(0.01)  # debounce delay
        if GPIO.input(encoderLeft) == GPIO.LOW:
            if right_state == GPIO.HIGH:
                current_mode = (current_mode + 1) % 3  # Next mode
            else:
                current_mode = (current_mode - 1) % 3  # Previous mode

def encoder_callback(channel):
    global current_mode
    state_right = GPIO.input(encoderRight)
    if state_right == GPIO.HIGH:
        current_mode = (current_mode + 1) % 3  # Next mode
    else:
        current_mode = (current_mode - 1) % 3

# main
if __name__ == "__main__":
    try:
        print("\nprogram start")

        # rejestracja eventów dla przycisków i enkodera
        # GPIO.add_event_detect(buttonRed, GPIO.FALLING, callback=button_pressed_callback, bouncetime=200)
        # GPIO.add_event_detect(buttonGreen, GPIO.FALLING, callback=button_pressed_callback, bouncetime=200)     
        GPIO.add_event_detect(encoderLeft, GPIO.FALLING, callback=encoder_callback, bouncetime=200)
        
        current_mode = 0  # (0 - temp, 1 - humid, 2 - press)

        while True:
            if GPIO.input(buttonRed) == GPIO.LOW:
                print("program exit")
                break
            #read_encoder()  # read encoder

            if current_mode == 0: # temperature
                temp = ds18b20()
                print(f"temperature: {temp} °C")
                visualize_temperature(temp)

            elif current_mode == 1: # humidity
                bme = bme280()
                humidity = bme.humidity
                #print(f"humidity: {humidity}.2f %")
                # round to 2 decimal places
                print(f"humidity: {humidity:.2f} %")
                visualize_humidity(humidity)

            elif current_mode == 2: # pressure
                bme = bme280()
                pressure = bme.pressure
                print(f"pressure: {pressure} hPa")
                visualize_pressure(pressure)

            time.sleep(1)

    except KeyboardInterrupt:
        print("\program interrupt")

    finally:
        pixels.fill((0, 0, 0))
        pixels.show()
        GPIO.cleanup()
        print("\nprogram finish")
