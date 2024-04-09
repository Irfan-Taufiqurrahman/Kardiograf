import random
import time
import logging
from django.conf import settings
from paho.mqtt import client as mqtt_client

logger = logging.getLogger(__name__)

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
    i = 0
    
    while True:
        random_data = [int(random.uniform(0, 100)) for _ in range(100)]  # Generate 100 random numbers
        message = ",".join(map(str, random_data)) + f",{i}"
        i += 1
        result = client.publish(topic, message)
        print(f"Message '{message}' published to topic '{topic}'")
        time.sleep(0.5)

def run():
    client = connect_mqtt()
    client.loop_start()
    publish(client)

if __name__ == '_main_':
    run()