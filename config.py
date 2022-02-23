import json


def ReadSessionId():
    with open("config.json") as f:
        return json.loads(f.read())["sessionId"]
