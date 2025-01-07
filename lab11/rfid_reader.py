import time
import RPi.GPIO as GPIO
from mfrc522 import MFRC522

import board
import neopixel

import config

class RfidReader:
    def __init__(self):
        self.reader = MFRC522()

        GPIO.output(config.buzzerPin, 0)

        self.pixels = neopixel.NeoPixel(
            pin=board.D8,
            n=8,
            brightness=0.2,
            auto_write=False
        )

    def beep(self, duration=0.1):
        GPIO.output(config.buzzerPin, 1)
        time.sleep(duration)
        GPIO.output(config.buzzerPin, 0)

    def set_color(self, r, g, b):
        self.pixels.fill((r, g, b))
        self.pixels.show()

    def reset_leds(self):
        self.set_color(0, 0, 0)

    def detect_card_once(self):
        print("Czekam na przyłożenie karty...")
        while True:
            status, TagType = self.reader.MFRC522_Request(self.reader.PICC_REQIDL)
            if status == self.reader.MI_OK:
                status, uid = self.reader.MFRC522_Anticoll()
                if status == self.reader.MI_OK:
                    uid_num = 0
                    for i in range(len(uid)):
                        uid_num += uid[i] << (i * 8)

                    now_str = time.strftime("%Y-%m-%d %H:%M:%S")

                    self.beep()
                    self.set_color(0, 255, 0)
                    time.sleep(1)
                    self.reset_leds()

                    while status == self.reader.MI_OK:
                        status, _ = self.reader.MFRC522_Anticoll()

                    return uid_num, uid, now_str
