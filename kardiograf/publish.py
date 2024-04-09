import random
import time
from paho.mqtt import client as mqtt_client

broker = 'broker.emqx.io'
port = 1883
topic = "ekg/ajik"

# Generate a Client ID with the publish prefix
client_id = f'publish-{random.randint(0, 100)}'

def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print(f"Failed to connect, return code {rc}")

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def publish(client):
    while True:
        message = f"{random.uniform(90, 120)},{random.uniform(90, 120)},{random.uniform(90, 120)}"
        result = client.publish(topic, message)
        print(f"Message '{message}' published to topic '{topic}'")
        time.sleep(2)

def run():
    client = connect_mqtt()
    client.loop_start()
    publish(client)

if __name__ == '__main__':
    run()
