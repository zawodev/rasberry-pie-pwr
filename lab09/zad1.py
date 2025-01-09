#!/usr/bin/env python3

from config import *
import RPi.GPIO as GPIO
import time

brightness = 50

def update_brightness(delta):
    global brightness
    brightness += delta
    if brightness > 100:
        brightness = 100
    if brightness < 0:
        brightness = 0
    diode1.ChangeDutyCycle(brightness)
    print(f"Current brightness: {brightness}%")

def encoder_callback(channel):
    state_right = GPIO.input(encoderRight)
    if state_right == GPIO.HIGH:
        update_brightness(-10)
    else:
        update_brightness(+10)

def main():
    global diode1

    diode1 = GPIO.PWM(led1, 50)
    diode1.start(brightness)

    GPIO.add_event_detect(encoderLeft, GPIO.FALLING, callback=encoder_callback, bouncetime=200)

    print("Turn the encoder to change brightness. Press Ctrl+C to exit.")

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        diode1.stop()
        GPIO.cleanup()
        print("\nProgram finished")

if __name__ == "__main__":
    main()
