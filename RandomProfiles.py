import gspread
from oauth2client.service_account import ServiceAccountCredentials
from jinja2 import Template
import random

token = "token.json"
sheet = "Random Profiles"


def initGspreadClient():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        token, scope)
    client = gspread.authorize(creds)
    return client


class RandomProfiles:
    def __init__(self):
        self.cl = initGspreadClient()
        self.MainSheet = self.cl.open(sheet).worksheet("Users")
        self.Users = self.MainSheet.col_values(1)[1:]

    def LoadUsers(self):
        self.Users = self.MainSheet.col_values(1)[1:]

    def GetRandomProfiles(self):
        return random.sample(self.Users, 10)
