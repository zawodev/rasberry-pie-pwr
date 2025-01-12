from config import *
import RPi.GPIO as GPIO
import time

def default_callback():
    pass

left_callback = default_callback
right_callback = default_callback

def encoder_callback(channel):
    state_right = GPIO.input(encoderRight)
    if state_right == GPIO.HIGH:
        left_callback()
    else:
        right_callback()
        
def assign_encoder_left_callback(callback):
    """przypisuje funkcję do lewego enkodera"""
    global left_callback
    left_callback = callback
    
def assign_encoder_right_callback(callback):
    """przypisuje funkcję do prawego enkodera"""
    global right_callback
    right_callback = callback

# konfiguracja enkoderów z obsługą zdarzeń
GPIO.add_event_detect(encoderLeft, GPIO.FALLING, callback=encoder_callback, bouncetime=200)
