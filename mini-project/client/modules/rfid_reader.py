import time
import RPi.GPIO as GPIO
from mfrc522 import MFRC522

import board
import neopixel

import config

reader = MFRC522()

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

class RfidReader:
    def __init__(self, callback):
        self.callback = callback

    def detect_card_once(self):
        while True:
            status, TagType = reader.MFRC522_Request(reader.PICC_REQIDL)
            if status == reader.MI_OK:
                status, uid = reader.MFRC522_Anticoll()
                if status == reader.MI_OK:
                    uid_num = 0
                    for i in range(len(uid)):
                        uid_num += uid[i] << (i*8)

                    now_str = time.strftime("%Y-%m-%d %H:%M:%S")
                    #print(f"Karta wykryta: UID={uid} ({uid_num}), czas: {now_str}")

                    self.callback(uid_num, uid, now_str)

                    while status == reader.MI_OK:
                        status, _ = reader.MFRC522_Anticoll()
