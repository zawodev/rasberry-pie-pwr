from admin_app import App
from mqtt_client import MqttClient

if __name__ == "__main__":
    import os
    path = os.path.join(os.getcwd(), "database.db")
    app = App(path)

    mqtt_client = MqttClient()

    def on_rfid_request(msg_str):
        print("Otrzymano żądanie RFID:", msg_str)
        app.add_request(msg_str)

        # sprawdzenie czy uzytkownik istnieje w bazie VALID, jak nie to dodanie do requests i zwrocenie INVALID

        mqtt_client.publish("RFID", "VALID") # albo INVALID


    def on_encoder_request(msg_str):
        print("Otrzymano żądanie ENCODER:", msg_str)
        app.add_request(msg_str)

        # sprawdzenie z sejfem z bazy dla danego uzytkowniak

        mqtt_client.publish("ENCODER_LOCK", "VALID") # albo INVALID


    mqtt_client.set_callback("RFID", on_rfid_request)
    mqtt_client.set_callback("ENCODER_LOCK", on_encoder_request)


    app.mainloop()
