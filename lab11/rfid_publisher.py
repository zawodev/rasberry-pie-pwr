import time
import paho.mqtt.client as mqtt

BROKER_ADDRESS = "localhost"
MQTT_TOPIC = "rfid/events"

from rfid_reader import RfidReader

def main():
    rfid = RfidReader()

    client = mqtt.Client()
    print(f"Łączenie z brokerem MQTT: {BROKER_ADDRESS}")
    client.connect(BROKER_ADDRESS)
    print("Połączono z brokerem MQTT.")

    try:
        while True:
            uid_num, uid_list, now_str = rfid.detect_card_once()

            msg_str = f"KARTA: {uid_num}, UID_LIST: {uid_list}, TIME: {now_str}"
            print(f"[PUB] Publikuję: {msg_str}")

            client.publish(MQTT_TOPIC, msg_str)

            time.sleep(0.2)

    except KeyboardInterrupt:
        print("Zatrzymano publikowanie (Ctrl+C).")

    finally:
        print("Rozłączanie z brokerem MQTT...")
        client.disconnect()

if __name__ == "__main__":
    main()
