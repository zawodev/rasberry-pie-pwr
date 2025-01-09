#!/usr/bin/env python3

import time
import config
import RPi.GPIO as GPIO

# Funkcja obsługująca debounce
def debounce(channel):
    time.sleep(0.05)  # Opóźnienie 50 ms na odbicie
    if GPIO.input(channel) == GPIO.LOW:
        if channel == config.buttonRed:
            print("Czerwony przycisk wciśnięty!")
        elif channel == config.buttonGreen:
            print("Zielony przycisk wciśnięty!")

# Konfiguracja przycisków z obsługą zdarzeń
GPIO.add_event_detect(config.buttonRed, GPIO.FALLING, callback=debounce, bouncetime=200)
GPIO.add_event_detect(config.buttonGreen, GPIO.FALLING, callback=debounce, bouncetime=200)

try:
    print("Czekam na wciśnięcia przycisków (naciśnij Ctrl+C, aby zakończyć)...")
    while True:
        time.sleep(1)  # Główna pętla może być "lekka"

except KeyboardInterrupt:
    print("\nZakończono program.")

finally:
    GPIO.cleanup()  # Zwalnianie zasobów GPIO po zakończeniu
