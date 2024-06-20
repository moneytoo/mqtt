import json
import paho.mqtt.client as mqtt
from light import Light

TOPIC_CABINET_DOOR = "zigbee2mqtt/living_room/cabinet/door"
TOPIC_CABINET_LIGHT = "zigbee2mqtt/living_room/cabinet/light"
TOPIC_TOILET_MOTION = "zigbee2mqtt/toilet/motion"
TOPIC_TOILET_LIGHT = "zigbee2mqtt/toilet/light"
TOPIC_BATHROOM_MOTION = "zigbee2mqtt/bathroom/motion"
TOPIC_BATHROOM_LIGHT = "zigbee2mqtt/bathroom/light"

LIGHT_OFF_CABINET = 15 * 60
LIGHT_OFF_ROOM = 5 * 60

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    client.subscribe(TOPIC_CABINET_DOOR)
    #client.subscribe(TOPIC_TOILET_MOTION)
    client.subscribe(TOPIC_TOILET_LIGHT)
    #client.subscribe(TOPIC_BATHROOM_MOTION)
    client.subscribe(TOPIC_BATHROOM_LIGHT)

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

    # Cabinet
    if msg.topic == TOPIC_CABINET_DOOR:
        payload = json.loads(msg.payload)
        if "contact" in payload:
            if payload["contact"] is False:
                cabinet_light.on()
            else:
                cabinet_light.off()

    # Toilet
    elif msg.topic == TOPIC_TOILET_MOTION:
        payload = json.loads(msg.payload)
        if "occupancy" in payload and payload["occupancy"]:
            toilet_light.on()
    elif msg.topic == TOPIC_TOILET_LIGHT:
        payload = json.loads(msg.payload)
        if "state" in payload:
            state = payload["state"]
            toilet_light.update_state(state)

    # Bathroom
    elif msg.topic == TOPIC_BATHROOM_MOTION:
        payload = json.loads(msg.payload)
        if "illuminance_lux" in payload:
            bathroom_light.update_lux(payload["illuminance_lux"])
        if "occupancy" in payload and payload["occupancy"]:
            bathroom_light.on_bathroom()
    elif msg.topic == TOPIC_BATHROOM_LIGHT:
        payload = json.loads(msg.payload)
        if "state" in payload:
            state = payload["state"]
            bathroom_light.update_state(state)


mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.connect("localhost", 1883, 60)

cabinet_light = Light(mqttc, TOPIC_CABINET_LIGHT, LIGHT_OFF_CABINET)
toilet_light = Light(mqttc, TOPIC_TOILET_LIGHT, LIGHT_OFF_ROOM)
bathroom_light = Light(mqttc, TOPIC_BATHROOM_LIGHT, LIGHT_OFF_ROOM)

mqttc.loop_forever()
