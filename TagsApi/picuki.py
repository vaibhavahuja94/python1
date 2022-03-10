import requests
from bs4 import BeautifulSoup
import re
import base64
import urllib.parse
import re

cookies = {
    '__atuvc': '11%7C6%2C36%7C7%2C8%7C8%2C43%7C9%2C4%7C10',
    '__atssc': 'google%3B1',
    '_ga_D9ZR5E8BN1': 'GS1.1.1646855338.33.1.1646855763.0',
    '_ga': 'GA1.2.354588203.1639393801',
    '__qca': 'P0-818663326-1639393804086',
    '__atuvs': '622904aaeb1c4754003',
    'aasd': '4%7C1646855339807',
    '__aaxsc': '1',
    '_gid': 'GA1.2.862167683.1646855340',
}

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'X-Requested-With': 'XMLHttpRequest',
    'Connection': 'keep-alive',
    'Referer': 'https://www.picuki.com/tag/memes',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'AlexaToolbar-ALX_NS_PH': 'AlexaToolbar/alx-4.0.2',
    'TE': 'trailers',
}


def getNextUrl(tag, soup, token):
    if not token:
        token = "HGJHGFHGDHGFHFDHDH"
    if loadDiv := soup.find("div", {"class": "load-more-wrapper"}):
        if len(l := loadDiv.get("data-next")) != 0:
            parser = urllib.parse.parse_qs(l)
            cursor = parser["end_cursor"][0]
            userId = parser["id"][0]
            return '/api/tags/{}/?cursor={}&token={}'.format(tag, cursor, token)
        else:
            return None
    elif loadDiv := soup.find("input", {"class": "pagination-next-page-input"}):
        if len(l := loadDiv.get("value")) != 0:
            parser = urllib.parse.parse_qs(l)
            cursor = parser["end_cursor"][0]
            userId = parser["id"][0]
            return '/api/tags/{}/?cursor={}&token={}'.format(tag, cursor, token)
        else:
            return None
    else:
        return None


def buildPicukiNextUrl(tag, cursor):
    return "https://www.picuki.com/app/controllers/ajax.php?type=tags&end_cursor={}&id={}".format(cursor, tag)


def getAllPostsJson(soup):
    posts = []
    for post in soup.find_all("div", {"class": "box-photo"}):
        if (p := getPostData(post)) != "ad":
            posts.append(p)
        else:
            pass
    return posts


def getPostData(p):
    if "adv" in p.attrs["class"]:
        return "ad"
    post = {}
    post["medias"] = []
    post['media_id'] = ''.join(re.findall(
        r'\d+', p.find("a").get("href").split("/")[-1]))
    if p.find("span", {"class": "flaticon-play-arrow"}):
        post["post_type"] = "video"
    else:
        post["post_type"] = "image"
    post["medias"].append({"url": proxyIt(
        p.find("img", {"class": 'post-image'}).get("src")), "type": "image"})
    post["content"] = p.find(
        "div", {"class": "photo-description"}).text.strip()
    post["likes"] = p.find("div", {"class": "likes_photo"}).text.strip()
    post["comments"] = p.find("div", {"class": "comments_photo"}).text.strip()
    post["date"] = p.find("div", {"class": "time"}).text.strip()
    return post


def proxyIt(url):
    return "https://my-proxy0.herokuapp.com/cdn?url="+base64.urlsafe_b64encode(url.encode()).decode("utf-8")


def getTagsDataFromPicuki(tag, cursor=None, token=None):
    data = {}
    if cursor:
        res = requests.get(buildPicukiNextUrl(tag, cursor),
                           headers=headers, cookies=cookies)

        if len(res.text) < 100:
            raise Exception("picui")
    else:
        res = requests.get(
            'https://www.picuki.com/tag/{}'.format(tag), headers=headers, cookies=cookies)
    soup = BeautifulSoup(res.text, "html.parser")
    data["has_next_page"] = False
    data["next_url"] = getNextUrl(tag, soup, token)
    if data["next_url"]:
        data["has_next_page"] = True
    data["posts"] = getAllPostsJson(soup)
    return data
