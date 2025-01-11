# main.py

from lib.rfid_reader import check_user
from lib.captcha import generate_captcha, verify_captcha
from lib.safe_lock import verify_combination
from lib.oled_display import display_message, display_progress
from lib.mqtt_client import send_verification_request
import config
import RPi.GPIO as GPIO
import time

# constants
time_to_reset = 5  # seconds to reset the process if verification fails

# main program
def main():
    try:
        while True:
            # step 1: check RFID card
            display_message("Scan your RFID card")
            rfid = check_user()
            if not rfid:
                display_message("Access Denied")
                buzz_failure()
                continue

            display_progress(1)

            # step 2: captcha verification
            display_message("Solve the captcha")
            captcha_data = generate_captcha()
            if not verify_captcha(captcha_data):
                display_message("Captcha failed")
                buzz_failure()
                continue

            display_progress(2)

            # step 3: safe combination verification
            display_message("Unlock the safe")
            if not verify_combination():
                display_message("Wrong combination")
                buzz_failure()
                continue

            display_progress(3)

            # step 4: final confirmation
            display_message("Press green button to continue")
            if not wait_for_green_button():
                display_message("Process cancelled")
                continue

            # send verification data to server
            response = send_verification_request(rfid)
            if response.get("status") != "success":
                display_message("Server verification failed")
                buzz_failure()
                continue

            display_message("Access Granted")
            display_progress(4)
            time.sleep(3)

    except KeyboardInterrupt:
        GPIO.cleanup()

# utility for green button
def wait_for_green_button():
    while True:
        if GPIO.input(config.buttonGreen) == GPIO.LOW:
            return True
        time.sleep(0.1)

# utility for buzzer
def buzz_failure():
    GPIO.output(config.buzzerPin, 0)
    time.sleep(0.5)
    GPIO.output(config.buzzerPin, 1)
    time.sleep(0.5)

if __name__ == "__main__":
    main()