# mqtt_publisher/management/commands/publish_mqtt.py
from django.core.management.base import BaseCommand
from kardiograf.mqtt_publisher import run  # Import the run function from mqtt_publisher.py

class Command(BaseCommand):
    help = 'Publishes MQTT messages'

    def handle(self, *args, **kwargs):
        run()  # Call the run function from mqtt_publisher.py
