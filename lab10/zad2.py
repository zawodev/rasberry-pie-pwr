import datetime

import time
from config import *
from mfrc522 import MFRC522
import board
import neopixel

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

def buzzer(state):
    GPIO.output(buzzerPin, not state)

pixels = neopixel.NeoPixel(board.D18, 8, brightness=0.2, auto_write=False)

def set_color(r, g, b):
    pixels.fill((r, g, b))
    pixels.show()

def reset_leds():
    pixels.fill((0, 0, 0))
    pixels.show()

def beep():
    buzzer(True)
    time.sleep(.1)
    buzzer(False)

reader = MFRC522()

try:
    print("czekam na przyłożenie karty...")
    while True:
        status, TagType = reader.MFRC522_Request(reader.PICC_REQIDL)
        if status == reader.MI_OK:
            status, uid = reader.MFRC522_Anticoll()
            if status == reader.MI_OK:
                uid_num = 0
                for i in range(len(uid)):
                    uid_num += uid[i] << (i*8)

                now = time.strftime("%Y-%m-%d %H:%M:%S")
                print(f"Karta wykryta: UID={uid} ({uid_num}), czas: {now}")
                
                beep()
                
                set_color(0, 255, 0)
                time.sleep(1)
                reset_leds()
                
                while status == reader.MI_OK:
                    status, _ = reader.MFRC522_Anticoll()

except KeyboardInterrupt:
    print("program przerwany")
finally:
    GPIO.cleanup()