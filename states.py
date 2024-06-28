import json
from topics import *

class States:
    def __init__(self, client):
        self.client = client
        self.states = {}

        for topic in [TOPIC_MARCEL_LIGHT, TOPIC_LIGHT_LIVING_ROOM, TOPIC_BATHROOM_LIGHT, TOPIC_TOILET_LIGHT]:
            self.client.publish(f"{topic}/get", json.dumps({"state":""}))

    def update_state(self, topic, state):
        self.states[topic] = state

    def is_on(self, topic):
        return self.states.get(topic, "OFF") == "ON"
