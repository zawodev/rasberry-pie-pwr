import time
import RPi.GPIO as GPIO
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
    time.sleep(1)
    buzzer(False)

def main():
    reader = MFRC522()
    last_uid = None
    card_present = False

    print("Czekam na przyłożenie karty RFID...")

    try:
        while True:
            (status, TagType) = reader.MFRC522_Request(reader.PICC_REQIDL)
            if status == reader.MI_OK:
                (status, uid) = reader.MFRC522_Anticoll()
                if status == reader.MI_OK:
                    uid_num = 0
                    for i in range(len(uid)):
                        uid_num += uid[i] << (i*8)

                    # Check if the card is the same as the last one
                    if not card_present or uid_num != last_uid:
                        now = time.strftime("%Y-%m-%d %H:%M:%S")
                        print(f"Karta wykryta: UID={uid} ({uid_num}), czas: {now}")

                        beep()

                        set_color(0, 255, 0)
                        time.sleep(1)
                        reset_leds()

                        last_uid = uid_num
                        card_present = True
                else:
                    print("Błąd odczytu UID")
            else:
                # If the card is not present, reset the last_uid
                if card_present:
                    card_present = False
                time.sleep(0.1)

    except KeyboardInterrupt:
        print("Zatrzymano program.")
    finally:
        reset_leds()
        GPIO.cleanup()

if __name__ == "__main__":
    main()
