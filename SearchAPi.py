import requests
from bs4 import BeautifulSoup
import base64


def proxyIt(url):
    return "https://my-proxy0.herokuapp.com/cdn?url="+base64.urlsafe_b64encode(url.encode()).decode("utf-8")


headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://dumpor.com/search?query=mohsin',
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


def SearchFromDumpor(query):
    response = requests.get(
        'https://dumpor.com/search?query={}'.format(query), headers=headers, allow_redirects=False)
    soup = BeautifulSoup(response.text, "html.parser")
    profiles, tags = [], []
    result = {}
    if navProfiles := soup.find("div", {"id": "nav-profiles"}):
        profiles = [{"user": x.text.strip()[1:], "profile":proxyIt(x.find("img").get("src"))} for x in navProfiles.find_all(
            "a", {"class": "profile-name-link"})]
    else:
        raise Exception("no profile nav")
    if navTags := soup.find("div", {"id": "nav-tags"}):
        tags = [x.text[1:] for x in navTags.find_all("a")]
    else:
        raise Exception("no tags nav")
    result["profiles"] = profiles
    result["tags"] = tags
    return result


def SearchFromPicuki(query):
    response = requests.get(
        "https://www.picuki.com/search/{}".format(query), headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    profiles, tags = [], []
    result = {}
    if navProfiles := soup.find("div", {"id": "search-profile-results"}):
        profiles = [{"user": x.get("title")[1:], "profile":proxyIt(x.find("img").get("src"))} for x in navProfiles.find_all(
            "div", {"class": "profile-result"})]
    else:
        raise Exception("no profiles nav picuki")
    if navTags := soup.find("div", {"id": "search-tags-results"}):
        tags = [x.text for x in navTags.find_all("a")]

    else:
        raise Exception("no tags nav picuki")
    result["profiles"] = profiles
    result["tags"] = tags
    return result


def Search(query):
    try:
        data = SearchFromPicuki(query=query)
        return data
    except Exception as e:
        print(e)
    try:
        data = SearchFromDumpor(query=query)
        return data
    except Exception as ex:
        print(ex)
        data = {"error": str(ex)}
    return data
