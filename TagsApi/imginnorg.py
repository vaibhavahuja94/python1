from bs4 import BeautifulSoup
import requests
import base64
from urllib.parse import urlparse
from urllib.parse import parse_qs
import timeago
import datetime

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/98.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'cross-site',
    'AlexaToolbar-ALX_NS_PH': 'AlexaToolbar/alx-4.0.2',
    'If-Modified-Since': 'Wed, 16 Mar 2022 16:18:52 GMT',
    'Cache-Control': 'max-age=0',
    'TE': 'trailers',
}


def proxyIt(url):
    return "https://my-proxy0.herokuapp.com/cdn?url="+base64.urlsafe_b64encode(url.encode()).decode("utf-8")


def getPostsJson(soup):
    postsJson = []
    if posts_c := soup.find({"div": "post-items"}):
        posts = posts_c.find_all("a", {"class": "item"})
        for p in posts:
            post = {}
            post['medias'] = []
            #
            imgUrl = p.find("img").get("data-src")
            post["medias"].append(
                {"url": proxyIt(getSrcFromUrl(imgUrl)), "type": "image"})
            #
            post["post_type"] = "video" if p.find("svg") else "image"
            post["content"] = p.find("img").get("alt")
            post["media_id"] = str(shortcode_to_id(
                p.get("href").split('/')[-2]))
            post["comments"] = ""
            post["likes"] = ""
            postsJson.append(post)
    return postsJson


def shortcode_to_id(shortcode):
    code = ('A' * (12-len(shortcode)))+shortcode
    return int.from_bytes(base64.b64decode(code.encode(), b'-_'), 'big')


def getSrcFromUrl(url):
    if "resize?url=" in url:
        return parse_qs(urlparse(url).query)['url'][0]
    else:
        return url.split("imginn.org/?")[-1]


def getNextUrl(soup=None, res=None, tag=None):
    if soup:
        if more := soup.find("a", {"class": "more-posts"}):
            return "/api/tags/{}/?cursor={}&token={}".format(tag, more.get("data-cursor"), "t")
    if res:
        if res["hasNext"]:
            return "/api/tags/{}/?cursor={}&token={}".format(tag, res["cursor"], "t")


def buildNexUrl(tag, cursor):
    return 'https://imginn.org/api/posts/?id={}&cursor={}&type=tag'.format(tag, cursor)


def GetDateFromTimestamp(timestamp):
    date = datetime.datetime.fromtimestamp(timestamp)
    return timeago.format(date, datetime.datetime.now())


def getNextData(res):
    resJson = res.json()
    posts = []
    for p in resJson["items"]:
        post = {}
        post["medias"] = []
        post["media_id"] = p["id"]
        post["post_type"] = "video" if p["isVideo"] else "image"
        post["content"] = p["alt"]
        post["medias"].append({"url": proxyIt(p['src']), "type": "image"})
        post["date"] = GetDateFromTimestamp(p["time"]/1000)
        post["comments"] = ""
        post["likes"] = ""
        posts.append(post)
    return posts


def getTagsFromImginn(tag=None, cursor=None):
    data = {}
    if cursor:
        res = requests.get(buildNexUrl(tag, cursor), headers=headers)
        if res.json()["code"] != 200:
            res = requests.get(buildNexUrl(tag, cursor), headers=headers)
        nextU = getNextUrl(None, res.json(), tag)
        data['has_next_url'] = True if nextU else False
        data["next_url"] = nextU
        data["posts"] = getNextData(res)

    else:
        res = requests.get(
            "https://imginn.org/tags/{}/".format(tag), headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        nextU = getNextUrl(soup, None, tag)
        data['has_next_url'] = True if nextU else False
        data["next_url"] = nextU
        data["posts"] = getPostsJson(soup)

    return data