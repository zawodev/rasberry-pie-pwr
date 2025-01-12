import time
from modules.rfid_reader import RfidReader

def default_callback(uid_num, uid_list, now_str):
    print(f"Karta wykryta: UID={uid_list} ({uid_num}), czas: {now_str}")

class RfidTest:
    def __init__(self):
        self.rfid_reader = RfidReader(default_callback)
        
    def run_once(self):
        self.rfid_reader.detect_card_once()
        
    def set_callback(self, callback):
        self.rfid_reader.callback = callback
