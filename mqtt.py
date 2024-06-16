import paho.mqtt.client as mqtt
from datetime import datetime, date, time, timezone
import json
import threading

auto_off_timer = None

TOPIC_CABINET_DOOR = "zigbee2mqtt/living_room/cabinet/door"
TOPIC_CABINET_LIGHT = "zigbee2mqtt/living_room/cabinet/light"

def light(client, topic, state):
    print("light")
    client.publish(f"{topic}/set", state)

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    client.subscribe(TOPIC_CABINET_DOOR)

def on_message(client, userdata, msg):
    global auto_off_timer
    print(msg.topic+" "+str(msg.payload))
    if msg.topic == TOPIC_CABINET_DOOR:
        payload = json.loads(msg.payload)
        contact = payload["contact"]
        if contact is True:
            print("is closed")
            light(client, TOPIC_CABINET_LIGHT, "OFF")
            if auto_off_timer is not None:
                auto_off_timer.cancel()
        else:
            print("is opened")
            light(client, TOPIC_CABINET_LIGHT, "ON")
            if auto_off_timer is not None:
                auto_off_timer.cancel()
            auto_off_timer = threading.Timer(15 * 60, light, args=[client, TOPIC_CABINET_LIGHT, "OFF"])
            auto_off_timer.start()

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.connect("localhost", 1883, 60)
mqttc.loop_forever()
