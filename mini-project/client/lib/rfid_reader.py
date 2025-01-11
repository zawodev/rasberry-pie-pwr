import time
import RPi.GPIO as GPIO
from mfrc522 import MFRC522

import board
import neopixel

import config

reader = MFRC522()

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

LED_COUNT = 8
LED_PIN = board.D18
LED_BRIGHTNESS = 1.0 / 32
pixels = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness=LED_BRIGHTNESS, auto_write=False)

def set_color(r, g, b):
    pixels.fill((r, g, b))
    pixels.show()

def beep():
    GPIO.output(config.buzzerPin, False)
    time.sleep(0.1)
    GPIO.output(config.buzzerPin, True)

class RfidReader:
    def __init__(self, publisher):
        self.publisher = publisher

    def detect_card_once(self):
        print("Czekam na przyłożenie karty...")
        while True:
            status, TagType = reader.MFRC522_Request(reader.PICC_REQIDL)
            if status == reader.MI_OK:
                status, uid = reader.MFRC522_Anticoll()
                if status == reader.MI_OK:
                    uid_num = 0
                    for i in range(len(uid)):
                        uid_num += uid[i] << (i*8)

                    now_str = time.strftime("%Y-%m-%d %H:%M:%S")
                    print(f"Karta wykryta: UID={uid} ({uid_num}), czas: {now_str}")

                    beep()

                    set_color(0, 255, 0)
                    time.sleep(1)
                    set_color(0, 0, 0)

                    self.publisher.publish(uid_num, uid, now_str)

                    while status == reader.MI_OK:
                        status, _ = reader.MFRC522_Anticoll()
