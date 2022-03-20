import requests
from bs4 import BeautifulSoup
import re
import json
import timeago
import datetime
import asyncio
import aiohttp
import config
import base64
import urllib.parse
import TagsApi.picuki as picuki
import TagsApi.dumpor as dumpor
import TagsApi.imginnorg as imginn
import TagsApi.instagram as instagram
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://dumpor.com/v/evofanclub',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'AlexaToolbar-ALX_NS_PH': 'AlexaToolbar/alx-4.0.2',
    'Cache-Control': 'max-age=0',
    'TE': 'trailers',
}


def getTags(tag, cursor="", token="", nextMedias=[]):
    try:
        return imginn.getTagsFromImginn(tag, cursor)
    except Exception as e:
        print(e)
    try:
        return picuki.getTagsDataFromPicuki(tag, cursor, token)
    except Exception as e:
        print(e)
    try:
        return instagram.GetInstaData(tag, cursor, token)
    except Exception as e:
        print(e)
    try:
        return asyncio.run(dumpor.GetData(tag, cursor, token))
    except Exception as e:
        print(e)
