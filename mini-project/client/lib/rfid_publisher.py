import time
import paho.mqtt.client as mqtt

BROKER_ADDRESS = "localhost"
MQTT_TOPIC = "rfid/events"

from rfid_reader import RfidReader

class Publisher:
    def __init__(self):
        self.rfid = RfidReader(self)
        self.client = mqtt.Client()
        print(f"Łączenie z brokerem MQTT: {BROKER_ADDRESS}")
        self.client.connect(BROKER_ADDRESS)
        print("Połączono z brokerem MQTT.")
    
    def run(self):
        try:
            while True:
                uid_num, uid_list, now_str = self.rfid.detect_card_once()

                msg_str = f"KARTA: {uid_num}, UID_LIST: {uid_list}, TIME: {now_str}"
                print(f"[PUB] Publikuję: {msg_str}")

                self.client.publish(MQTT_TOPIC, msg_str)

                time.sleep(0.2)

        except KeyboardInterrupt:
            print("Zatrzymano publikowanie (Ctrl+C).")

        finally:
            print("Rozłączanie z brokerem MQTT...")
            self.client.disconnect()
            
    def publish(self, uid_num, uid_list, now_str):
        msg_str = f"KARTA: {uid_num}, UID_LIST: {uid_list}, TIME: {now_str}"
        print(f"[PUB] Publikuję: {msg_str}")

        self.client.publish(MQTT_TOPIC, msg_str)

        time.sleep(0.2)
        
if __name__ == "__main__":
    publisher = Publisher()
    publisher.run()
    
