from config import *
import Rpi.GPIO as GPIO
import time

diodes = []
diodes.append(GPIO.PWM(led1, 50))
diodes.append(GPIO.PWM(led2, 50))
diodes.append(GPIO.PWM(led3, 50))
diodes.append(GPIO.PWM(led4, 50))

for diode in diodes:
    diode.start(0)
    
def display_progress(progress):
    for i in range(4):
        if i < progress:
            diodes[i].ChangeDutyCycle(100)
        else:
            diodes[i].ChangeDutyCycle(0)
