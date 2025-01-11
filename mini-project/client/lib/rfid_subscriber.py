import time
import paho.mqtt.client as mqtt

BROKER_ADDRESS = "localhost"
MQTT_TOPIC = "rfid/events"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Połączono z brokerem MQTT.")
        print("Subskrypcja tematu:", MQTT_TOPIC)
        client.subscribe(MQTT_TOPIC)
    else:
        print("Błąd połączenia. Kod =", rc)

def on_message(client, userdata, msg):
    payload_str = msg.payload.decode("utf-8")
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Otrzymano: {payload_str}")

def main():
    client = mqtt.Client()

    client.on_connect = on_connect
    client.on_message = on_message

    print(f"Łączenie z brokerem: {BROKER_ADDRESS} ...")
    client.connect(BROKER_ADDRESS, port=1883, keepalive=60)

    client.loop_forever()

if __name__ == "__main__":
    main()