import paho.mqtt.client as mqtt
from datetime import datetime, date, time, timezone
import json
import threading

auto_off_timer = None

TOPIC_CABINET_DOOR = "zigbee2mqtt/living_room/cabinet/door"
TOPIC_CABINET_LIGHT = "zigbee2mqtt/living_room/cabinet/light"

def light(client, topic, state, brightness=None):
    print("light")
    payload = {"state": state}
    if brightness is not None:
        payload["brightness"] = brightness
    client.publish(f"{topic}/set", json.dumps(payload))

def handle_cabinet_door(client, contact, timer):
    if contact is False:
        light(client, TOPIC_CABINET_LIGHT, "ON", 255)
        if timer is not None:
            timer.cancel()
        timer = threading.Timer(15 * 60, light, args=[client, TOPIC_CABINET_LIGHT, "OFF"])
        timer.start()
    else:
        light(client, TOPIC_CABINET_LIGHT, "OFF")
        if timer is not None:
            timer.cancel()

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    client.subscribe(TOPIC_CABINET_DOOR)

def on_message(client, userdata, msg):
    global auto_off_timer
    print(msg.topic+" "+str(msg.payload))
    if msg.topic == TOPIC_CABINET_DOOR:
        payload = json.loads(msg.payload)
        contact = payload["contact"]
        handle_cabinet_door(client, contact, auto_off_timer)


mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.connect("localhost", 1883, 60)
mqttc.loop_forever()
