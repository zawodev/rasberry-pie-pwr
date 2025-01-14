import time
import paho.mqtt.client as mqtt

BROKER_ADDRESS = "localhost"
RFID_POST_TOPIC = "client/rfid"
ENCODER_LOCK_POST_TOPIC = "client/encoder_lock"
RESPONSE_GET_TOPIC = "server/response"

def default_callback(msg):
    print("default_callback: ", msg)
    pass

class MqttClient:
    def __init__(self):
        self.client = mqtt.Client()
        print(f"Łączenie z brokerem MQTT: {BROKER_ADDRESS}")
        self.client.connect(BROKER_ADDRESS)
        print("Połączono z brokerem MQTT.")
        self.callback = default_callback
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.loop_start()

    def publish(self, topic, msg_str):
        self.client.publish(topic, msg_str)
        
    def set_callback(self, callback):
        self.callback = callback
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Połączono z brokerem MQTT. Subskrypcja tematu:", RESPONSE_GET_TOPIC)
            client.subscribe(RESPONSE_GET_TOPIC)
        else:
            print("Błąd połączenia. Kod=", rc)
            
    def on_message(self, client, userdata, msg):
        self.callback(msg.payload.decode("utf-8"))
        