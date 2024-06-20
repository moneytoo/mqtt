import json

def control_light(client, topic, state, brightness=None):
    payload = {"state": state}
    if brightness is not None:
        payload["brightness"] = brightness
    client.publish(f"{topic}/set", json.dumps(payload))
