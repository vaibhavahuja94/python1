import requests
from bs4 import BeautifulSoup
import base64
import config

cdn = config.Getcdn()


def proxyIt(url):
    return cdn+base64.urlsafe_b64encode(url.encode()).decode("utf-8")


headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Referer': 'https://gramhir.com/profile/asharqnews/13136729029',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'AlexaToolbar-ALX_NS_PH': 'AlexaToolbar/alx-4.0.2',
    'TE': 'trailers',
}


def getGramhirVideoLink(idd):
    response = requests.get(
        'https://gramhir.com/media/{}'.format(idd), headers=headers)
    sp = BeautifulSoup(response.text, "html.parser")
    if div := sp.find("div", {"class": "single-photo"}):
        if video := div.find("video"):
            return proxyIt(video.find("source").get("src"))


def getPicukiVideoLink(idd):
    response = requests.get(
        'https://www.picuki.com/media/{}'.format(idd), headers=headers)
    sp = BeautifulSoup(response.text, "html.parser")
    if div := sp.find("div", {"class": "single-photo"}):
        if video := div.find("video"):
            return proxyIt(video.get("src"))


def getDumporVideoLink(idd):
    res = requests.get('https://dumpor.com/c/'+idd[::-1], headers=headers)
    sp = BeautifulSoup(res.text, "html.parser")
    if video := sp.find("div", {"class": "video-container"}):
        return proxyIt(video.find("video").get("src"))


def getVideoLink(idd):
    if video := getGramhirVideoLink(idd):
        return video
    elif video := getPicukiVideoLink(idd):
        return video
    elif video := getDumporVideoLink(idd):
        return video
    else:
        return None
