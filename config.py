import json


def ReadSessionId():
    with open("config.json") as f:
        return json.loads(f.read())["sessionId"]


def Getcdn():
    with open("config.json") as f:
        return json.loads(f.read())["cdn"]+"/cdn?url="
