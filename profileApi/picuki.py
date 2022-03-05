import requests
from bs4 import BeautifulSoup
import re
import base64
import urllib.parse
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://www.picuki.com/search/evofanclub',
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


def getNextUrl(soup, token):
    if not token:
        token = "HGJHGFHGDHGFHFDHDH"
    if loadDiv := soup.find("div", {"class": "load-more-wrapper"}):
        if len(l := loadDiv.get("data-next")) != 0:
            parser = urllib.parse.parse_qs(l)
            cursor = parser["end_cursor"][0]
            userId = parser["id"][0]
            return '/api/profile/{}/?cursor={}&token={}'.format(userId, cursor, token)
        else:
            return None
    elif loadDiv := soup.find("input", {"class": "pagination-next-page-input"}):
        if len(l := loadDiv.get("value")) != 0:
            parser = urllib.parse.parse_qs(l)
            cursor = parser["end_cursor"][0]
            userId = parser["id"][0]
            return '/api/profile/{}/?cursor={}&token={}'.format(userId, cursor, token)
        else:
            return None
    else:
        return None


def buildPicukiNextUrl(userId, cursor):
    return "https://www.picuki.com/app/controllers/ajax.php?type=profile&end_cursor={}&id={}".format(cursor, userId)


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
    post['media_id'] = ''.join(re.findall(r'\d+', p.find("a").get("href").split("/")[-1]))
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


def BuildStories(soup, username):
    userId = re.findall(r"query = '(.*)';", str(soup))[0]
    return "/api/stories/{}/{}/".format(userId, username)


def getUserData(soup):
    profile_info = soup.find("div", {"class": "profile-info"})
    userImage = proxyIt(profile_info.find(
        "div", {"class": "profile-avatar"}).find("a").get("data-video-poster"))
    userTitle = profile_info.find(
        "h2", {"class": "profile-name-bottom"}).text.strip()
    userName = profile_info.find(
        "h1", {"class": "profile-name-top"}).text.strip()[1:]
    description = soup.find(
        "div", {"class": "profile-description"}).text.strip()
    ct = soup.find("div", {"class": "content-title"})
    numberOfPosts = ''.join(re.findall(
        r'\d+', ct.find("span", {"class": "total_posts"}).text))
    followers = ''.join(re.findall(
        r'\d+', ct.find("span", {"class": "followed_by"}).text))
    following = ''.join(re.findall(
        r'\d+', ct.find("span", {"class": "follows"}).text))
    user = {}
    user["ProfileImage"] = userImage
    user["Title"] = userTitle
    user["Username"] = userName
    user["TotalPosts"] = numberOfPosts
    user["Followers"] = followers
    user["Following"] = following
    user["Desc"] = description
    user["stories"] = BuildStories(soup, userName)
    return user


def getDataFromPicuki(username, userId=None, cursor=None, token=None):
    data = {}
    if cursor:
        res = requests.get(buildPicukiNextUrl(userId, cursor), headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
    else:
        res = requests.get(
            'https://www.picuki.com/profile/{}'.format(username), headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        data["UserData"] = getUserData(soup)
    data["has_next_page"] = False
    data["next_url"] = getNextUrl(soup, token)
    if data["next_url"]:
        data["has_next_page"] = True
    data["posts"] = getAllPostsJson(soup)
    return data
