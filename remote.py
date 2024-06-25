import json
from utils import control_light, control_light_step

STEP = 16

class Remote:
    def __init__(self, client, topic_light):
        self.client = client
        self.topic_light = topic_light
        self.state = None

        self.client.publish(f"{self.topic_light}/get", json.dumps({"state":""}))

    def update_state(self, state):
        print(f"State: {state}")
        self.state = state

    def action(self, action):
        print(f"Action: {action}")
        if action == "on_press":
            control_light(self.client, self.topic_light, "toggle")
        elif action == "up_press":
            if self.state is None or self.state == "ON":
                control_light_step(self.client, self.topic_light, STEP)
            else:
                control_light(self.client, self.topic_light, "ON", brightness=255)
        elif action == "down_press":
            if self.state is None or self.state == "ON":
                control_light_step(self.client, self.topic_light, - STEP)
            else:
                control_light(self.client, self.topic_light, "ON", brightness=16)
        elif action == "off_press":
            control_light(self.client, self.topic_light, "ON", brightness=128)
        elif action == "up_hold":
            control_light(self.client, self.topic_light, "ON", brightness=255)
        elif action == "down_hold":
            control_light(self.client, self.topic_light, "ON", brightness=16)
