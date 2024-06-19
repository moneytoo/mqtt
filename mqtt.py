import paho.mqtt.client as mqtt
from datetime import datetime, date, time, timezone, timedelta
import json
import threading
from sun_times import SunTimes

TOPIC_CABINET_DOOR = "zigbee2mqtt/living_room/cabinet/door"
TOPIC_CABINET_LIGHT = "zigbee2mqtt/living_room/cabinet/light"
TOPIC_TOILET_MOTION = "zigbee2mqtt/toilet/motion"
TOPIC_TOILET_LIGHT = "zigbee2mqtt/toilet/light"
TOPIC_BATHROOM_MOTION = "zigbee2mqtt/bathroom/motion"
TOPIC_BATHROOM_LIGHT = "zigbee2mqtt/bathroom/light"

LIGHT_OFF_CABINET = 15 * 60
LIGHT_OFF_ROOM = 5 * 60
DIM_DURATION = 20

class Light:
    sun_times = SunTimes()

    def __init__(self, client, topic, off_time):
        self.client = client
        self.topic = topic
        self.off_time = off_time
        self.timer_dim = None
        self.timer_off = None
        self.state = None
        self.lux = 0

    def __timers_cancel(self):
        if self.timer_dim is not None:
            self.timer_dim.cancel()
        if self.timer_off is not None:
            self.timer_off.cancel()

    def __dim(self):
        control_light(self.client, self.topic, "ON", brightness=64)  # 25% of 255

    def update_state(self, state):
        self.state = state

    def update_lux(self, lux):
        self.lux = lux

    def on(self):
        # Turn on light only if it's not already on.
        # This is to prevent reseting the light settings (like brightness).
        if self.state is None or self.state == "OFF":
            control_light(self.client, self.topic, "ON", brightness=255)
        # Light is on now, so start the off timers.
        self.__timers_cancel()
        self.timer_dim = threading.Timer(self.off_time - DIM_DURATION, self.__dim)
        self.timer_off = threading.Timer(self.off_time, self.off)
        self.timer_dim.start()
        self.timer_off.start()

    def on_bathroom(self):
        # During night or low light
        if self.sun_times.is_night() or self.lux < 150:
            self.on()
        # TODO: If light is already on, reset timers

        # TODO: sun light check
        if self.lux < 150:
            #self.on()
            self.__timers_cancel()
            self.timer_dim = threading.Timer(self.off_time - DIM_DURATION, self.__dim)
            self.timer_off = threading.Timer(self.off_time, self.off)
            self.timer_dim.start()
            self.timer_off.start()

    def off(self):
        self.__timers_cancel()
        control_light(self.client, self.topic, "OFF")

def control_light(client, topic, state, brightness=None):
    payload = {"state": state}
    if brightness is not None:
        payload["brightness"] = brightness
    client.publish(f"{topic}/set", json.dumps(payload))

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    client.subscribe(TOPIC_CABINET_DOOR)
    #client.subscribe(TOPIC_TOILET_MOTION)
    client.subscribe(TOPIC_TOILET_LIGHT)
    #client.subscribe(TOPIC_BATHROOM_MOTION)
    client.subscribe(TOPIC_BATHROOM_LIGHT)

def on_message(client, userdata, msg):
    global timer_cabinet, timer_toilet
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
        if "occupancy" in payload:
            if payload["occupancy"]:
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
        if "occupancy" in payload:
            if payload["occupancy"]:
                bathroom_light.on()
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
