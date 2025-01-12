import time
import threading
import neopixel
import board

from lab09.zad1 import brightness
from modules.buttons import assign_red_button_callback, assign_green_button_callback
from modules.buzzer import buzz_once
from modules.encoder import assign_encoder_left_callback, assign_encoder_right_callback
import modules.lib.oled.SSD1331 as SSD1331

from mqtt_client import MqttClient

from rfid_test import RfidTest
from captcha import Captcha
from encoder_lock import EncoderLock

class Safe:
    def __init__(self):
        self.mqtt_client = MqttClient()
        self.pixels = neopixel.NeoPixel(board.D18, 8, brightness=1.0/32, auto_write=False)
        self.display = SSD1331.SSD1331()
        self.display.Init()
        
        self.rfid_test = RfidTest()
        self.captcha = Captcha(self.display)
        self.encoder_lock = EncoderLock(self.pixels, [55, 161, 21, 11, 222, 0, 255, 65])
        
        self.current_test = 0
        self.last_activity_time = time.time()
        self.timeout_seconds = 60

        self.running = True
        self.setup_idle_timeout()

    def setup_idle_timeout(self):
        def monitor_timeout():
            while self.running:
                if time.time() - self.last_activity_time > self.timeout_seconds:
                    self.reset_to_start()
                time.sleep(1)

        threading.Thread(target=monitor_timeout, daemon=True).start()

    def record_activity(self):
        self.last_activity_time = time.time()

    def start(self):
        self.reset_to_start()
        while self.running:
            time.sleep(0.1)

    def reset_to_start(self):
        self.current_test = 0
        self.display.clear()
        self.display.ShowImage("modules/lib/oled/locked.png", 0, 0)
        time.sleep(2)
        self.setup_rfid_test()

    def setup_rfid_test(self):
        def handle_server_response(response):
            if response == "VALID":
                self.current_test = 1
                self.setup_captcha_test()
            elif response == "INVALID":
                buzz_once()
                self.rfid_test.run_once() # nie wiem czy konieczne?
            else:
                buzz_once()
                buzz_once()
                print("unknown response from server:", response)
                
        def on_card_scanned(uid_num, uid_list, now_str):
            self.record_activity()

            self.mqtt_client.set_callback(handle_server_response)
            
            msg_str = f"KARTA: {uid_num}, UID_LIST: {uid_list}, TIME: {now_str}"
            self.mqtt_client.publish(msg_str)
                
        self.rfid_test.set_callback(on_card_scanned)
        self.rfid_test.run_once()
        self.display.ShowImage("modules/lib/oled/test1_rfid.png", 0, 0)

    def setup_captcha_test(self):
        assign_encoder_left_callback(lambda: self.captcha.translate_piece(-1))
        assign_encoder_right_callback(lambda: self.captcha.translate_piece(1))

        def on_confirm():
            self.record_activity()
            if self.captcha.confirm_position():
                self.current_test = 2
                self.setup_encoder_lock_test()
            else:
                buzz_once()

        assign_red_button_callback(lambda: self.captcha.switch_axis())
        assign_green_button_callback(on_confirm)
        self.captcha.display.ShowImage("lib/oled/captcha_test.png", 0, 0)

    def setup_encoder_lock_test(self):
        assign_encoder_left_callback(self.encoder_lock.encoder_left_callback)
        assign_encoder_right_callback(self.encoder_lock.encoder_right_callback)
        assign_red_button_callback(self.encoder_lock.red_button_callback)
        assign_green_button_callback(self.encoder_lock.green_button_callback)
        
        def on_confirm():
            self.record_activity()
            if self.encoder_lock.confirm_solution():
                self.encoder_lock.running = False
                self.current_test = 3
                self.setup_button_test()
            else:
                buzz_once()
                
        self.encoder_lock.assign_confirm_callback(on_confirm)
        self.captcha.display.ShowImage("lib/oled/safe_lock_test.png", 0, 0)
        self.encoder_lock.run()

    def setup_button_test(self):
        def on_green_pressed():
            self.record_activity()
            self.on_success()

        assign_green_button_callback(on_green_pressed)
        self.captcha.display.ShowImage("lib/oled/press_green.png", 0, 0)

    def on_success(self):
        self.captcha.display.ShowImage("lib/oled/success.png", 0, 0)
        print("Access granted!")
        self.running = False

if __name__ == "__main__":
    safe = Safe()
    safe.start()
