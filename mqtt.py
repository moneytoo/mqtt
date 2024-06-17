import paho.mqtt.client as mqtt
from datetime import datetime, date, time, timezone
import json
import threading

timer_cabinet = None
timer_toilet = None

TOPIC_CABINET_DOOR = "zigbee2mqtt/living_room/cabinet/door"
TOPIC_CABINET_LIGHT = "zigbee2mqtt/living_room/cabinet/light"
TOPIC_TOILET_MOTION = "zigbee2mqtt/toilet/motion"

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

def handle_room_motion(client, topic, timer):
    light(client, topic, "ON", 255)
    if timer is not None:
        timer.cancel()
    timer = threading.Timer(5 * 60, light, args=[client, topic, "OFF"])
    timer.start()

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    client.subscribe(TOPIC_CABINET_DOOR)
    #client.subscribe(TOPIC_TOILET_MOTION)

def on_message(client, userdata, msg):
    global timer_cabinet, timer_toilet
    print(msg.topic+" "+str(msg.payload))
    if msg.topic == TOPIC_CABINET_DOOR:
        payload = json.loads(msg.payload)
        if "contact" in payload:
            handle_cabinet_door(client, payload["contact"], timer_cabinet)
    elif msg.topic == TOPIC_TOILET_MOTION:
        payload = json.loads(msg.payload)
        if "occupancy" in payload:
            if payload["occupancy"]:
                handle_room_motion(client, TOPIC_TOILET_MOTION, timer_toilet)


mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.connect("localhost", 1883, 60)
mqttc.loop_forever()
