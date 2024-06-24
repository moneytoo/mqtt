from utils import control_light, control_light_step

class Remote:
    def __init__(self, client, topic_light):
        self.client = client
        self.topic_light = topic_light

    def action(self, action):
        print(f"Action: {action}")
        if action == "on_press":
            control_light(self.client, self.topic_light, "toggle")
        elif action == "up_press":
            control_light_step(self.client, self.topic_light, 16)
        elif action == "down_press":
            control_light_step(self.client, self.topic_light, -16)
        elif action == "off_press":
            control_light(self.client, self.topic_light, "ON", brightness=128)
