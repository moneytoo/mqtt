import paho.mqtt.client as mqtt
from datetime import datetime, date, time, timezone
import json
import threading

auto_off_timer = None

def light(client, topic, state):
    print("light")
    client.publish(f"zigbee2mqtt/{topic}/set", state)

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    client.subscribe("zigbee2mqtt/living_room/cabinet/door")

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    if msg.topic == "zigbee2mqtt/living_room/cabinet/door":
        print(datetime.now().isoformat(timespec='milliseconds'))
        payload = json.loads(msg.payload)
        contact = payload["contact"]
        if contact is True:
            print("is closed")
            light(client, "living_room/marcel/light", "OFF")
        else:
            print("is opened")
            light(client, "living_room/marcel/light", "ON")
            #auto_off_timer = threading.Timer(15 * 60, light, args=[])

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.connect("localhost", 1883, 60)
mqttc.loop_forever()
