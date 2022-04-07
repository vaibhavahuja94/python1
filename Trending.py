from google.oauth2 import service_account
from googleapiclient.discovery import build
import requests
import json
import datetime
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials

token = "token.json"
sheet = "Trending Profile"


def initGspreadClient():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        token, scope)
    client = gspread.authorize(creds)
    return client


def Update():
    cl = initGspreadClient()
    mainSheet = cl.open(sheet)
    trending = mainSheet.worksheet("Trending")
    popular = mainSheet.worksheet("Popular")
    data = {}
    data["trending"] = trending.get_all_records()
    data["popular"] = popular.get_all_records()
    with open("trend.json", "w") as f:
        f.write(json.dumps(data))
