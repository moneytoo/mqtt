import json
import threading
from utils import control_light
from sun_times import SunTimes

DIM_DURATION = 20

class Light:
    sun_times = SunTimes()

    def __init__(self, client, topic, off_time, topic_door=None):
        self.client = client
        self.topic = topic
        self.off_time = off_time
        self.topic_door = topic_door
        self.timer_dim = None
        self.timer_off = None
        self.state = None
        self.lux = 0
        self.door_closed = False

        self.client.publish(f"{self.topic}/get", json.dumps({"state":""}))
        self.client.publish(f"{self.topic_door}/get", json.dumps({"contact":False}))

    def __timers_cancel(self):
        if self.timer_dim is not None:
            self.timer_dim.cancel()
        if self.timer_off is not None:
            self.timer_off.cancel()

    def __timers_start(self):
        self.timer_dim = threading.Timer(self.off_time - DIM_DURATION, self.__dim)
        self.timer_off = threading.Timer(self.off_time, self.off)
        self.timer_dim.start()
        self.timer_off.start()

    def __timers_restart(self):
        print("Restarting timers")
        self.__timers_cancel()
        self.__timers_start()

    def __dim(self):
        control_light(self.client, self.topic, "ON", brightness=64)  # 25% of 255

    def update_state(self, state):
        self.state = state

    def update_lux(self, lux):
        self.lux = lux

    # def update_door(self, door_closed):
    #     print(f"Door closed: {door_closed}")
    #     self.door_closed = door_closed
    #     if self.topic_door is not None and not self.door_closed:
    #         self.__timers_restart()
    #     # TODO: Close will turn on the light early

    def on(self):
        # Turn on light only if it's not already on.
        # This is to prevent reseting the light settings (like brightness).
        if self.state is None or self.state == "OFF":
            control_light(self.client, self.topic, "ON", brightness=255)
        # Light is on now
        # No timers if door is closed
        if self.topic_door is not None and self.door_closed:
            self.__timers_cancel()
        # Start the off timers
        else:
            self.__timers_restart()

    def on_bathroom(self):
        # During night or low light
        if self.sun_times.is_night() or self.lux < 150:
            # Turn on as well as start the off timers
            self.on()
        elif self.state is not None and self.state == "ON":
            self.__timers_restart()

    def off(self):
        self.__timers_cancel()
        control_light(self.client, self.topic, "OFF")
