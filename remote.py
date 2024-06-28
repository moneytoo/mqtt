from utils import control_light, control_light_step
from topics import TOPIC_MARCEL_LIGHT, TOPIC_LIGHT_LIVING_ROOM, TOPIC_LIGHT_JANA, TOPIC_LIGHT_TABLE

STEP = 32

class Remote:
    def __init__(self, client, states):
        self.client = client
        self.states = states

    def action(self, action):
        print(f"Action: {action}")
        if action == "on_press":
            control_light(self.client, TOPIC_MARCEL_LIGHT, "toggle")
        elif action == "up_press":
            if self.states.is_on(TOPIC_MARCEL_LIGHT):
                control_light_step(self.client, TOPIC_MARCEL_LIGHT, STEP)
            else:
                control_light(self.client, TOPIC_MARCEL_LIGHT, "ON", brightness=255)
        elif action == "down_press":
            if self.states.is_on(TOPIC_MARCEL_LIGHT):
                control_light_step(self.client, TOPIC_MARCEL_LIGHT, - STEP)
            else:
                control_light(self.client, TOPIC_MARCEL_LIGHT, "ON", brightness=16)
        elif action == "off_press":
            control_light(self.client, TOPIC_MARCEL_LIGHT, "ON", brightness=128)
        elif action == "up_hold":
            control_light(self.client, TOPIC_MARCEL_LIGHT, "ON", brightness=255)
        elif action == "down_hold":
            control_light(self.client, TOPIC_MARCEL_LIGHT, "ON", brightness=16)

    def action_ikea(self, action):
        print(f"Action: {action}")
        if action == "on":
            control_light(self.client, TOPIC_LIGHT_LIVING_ROOM, "toggle")
        elif action == "arrow_right_click":
            control_light(self.client, TOPIC_MARCEL_LIGHT, "toggle")
        elif action == "arrow_left_click":
            control_light(self.client, TOPIC_LIGHT_JANA, "toggle")
        elif action == "off":
            control_light(self.client, TOPIC_LIGHT_TABLE, "toggle")
