import re
import requests
from bs4 import BeautifulSoup
import asyncio
import aiohttp
import base64
import urllib.parse

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


async def getDumporVideoLink(session, idd):
    print("start", idd)
    async with session.get('https://dumpor.com/c/'+idd) as r:
        # res = requests.get('https://mohsiss-proxy0.herokuapp.com/?url=https://dumpor.com/c/'+idd, headers=headers)
        content = await r.read()
        print("done", idd)
        sp = BeautifulSoup(content, "html.parser")
        if video := sp.find("div", {"class": "video-container"}):
            return video.find("video").get("src")
        return None


def ExtractUrlFromDumpor(l):
    parser = urllib.parse.parse_qs(l)
    s = parser[list(parser.keys())[0]][0][::-1]
    # url=base64.decodebytes(bytes(s,"utf-8")).decode("utf-8")
    return s


def GetNextUrl(userId, soup):
    cursor = ""
    token = ""
    if LoadDiv := soup.find("div", {"id": "load_more"}):
        cursor = LoadDiv.get("data-cursor")
        token = LoadDiv.get("data-token")
        userId = LoadDiv.get("data-name")
        if cursor != "":
            return "/api/profile/{}/?cursor={}&token={}".format(userId, cursor, token)
        else:
            return None
    else:
        return None


def BuildNextUrl(userId, cursor, token):
    return "https://dumpor.com/api/profile/{}/?cursor={}&token={}".format(userId, cursor, token)


def BuildNextInstUrl(userId, cursor, token):
    return "/api/profile/{}/?cursor={}&token={}".format(userId, cursor, token)


async def ExtractPostData(session, Post, showVideo=False):
    if Post.find("div", {"class": "content__img-wrap"}):
        post = {}
        post["medias"] = []
        post['media_id'] = int(Post.find("a").get("href").split("/")[-1][::-1])
        if Post.find("div", {"class": "video-icon"}) != None:
            post['post_type'] = "video"
            if showVideo:
                v = await getDumporVideoLink(session, post['media_id'][::-1])
                post["medias"].append(
                    {"url": "https://my-proxy0.herokuapp.com/cdn?url=" + ExtractUrlFromDumpor(v), "type": "video"})

        else:
            post['post_type'] = "image"
        post["medias"].append(
            {"url": "https://my-proxy0.herokuapp.com/cdn?url=" + ExtractUrlFromDumpor(Post.find("img").get("src")), "type": "image"})
        post["content"] = Post.find("div", {"class": "content__text"}).text
        Btns = Post.find("div", {"class": "content__btns"}).find_all("div")
        post["likes"], post["comments"], post["date"] = Btns[0].find(
            "span").text, Btns[1].find("span").text, Btns[2].find("span").text
        return post
    if Post.find("div", {"class": "ads_content"}):
        return "ad"


async def ExtractProfilePosts(soup):
    # PostsList=[]
    # if PostsC:=soup.find("div",{"class":"content__list"}):
    PostsList = soup.find_all("div", {"class": "content__item"})
    PostsJson = []
    async with aiohttp.ClientSession(headers=headers) as session:
        ##
        tasks = []
        for Post in PostsList:
            tasks.append(asyncio.ensure_future(ExtractPostData(session, Post)))
        for x in await asyncio.gather(*tasks):
            if x != "ad" and x != None:
                PostsJson.append(x)
    return PostsJson


##
def shortcode_to_id(shortcode):
    code = ('A' * (12-len(shortcode)))+shortcode
    return int.from_bytes(base64.b64decode(code.encode(), b'-_'), 'big')


def EncodeUrl(url):
    return base64.urlsafe_b64encode(bytes(url, 'utf-8')).decode("UTF-8")


def GetUserId(soup):
    if StoriesC := soup.find("div", {"id": "stories-container"}):
        return StoriesC.get("data-remote-id")
    else:
        return None


def BuildStories(soup, username):
    userId = soup.find(
        "div", {"id": "stories-container"}).get("data-remote-id")
    token = soup.find(
        "div", {"id": "stories-container"}).get("data-token")
    return "/api/stories/{}/{}/?token={}".format(userId, username, token)


def GetUserData(soup):
    user = {}
    if userDiv := soup.find("div", {"class": "user"}):
        userImage = userDiv.find('div', {"class": "user__img"}).get('style')
        userImage = "https://my-proxy0.herokuapp.com/cdn?url=" + \
            ExtractUrlFromDumpor(
                userImage[userImage.index("url('")+5:len(userImage)-3])
        userTitle = userDiv.find(
            "div", {"class": "user__title"}).find("h1").text
        userName = userDiv.find(
            "div", {"class": "user__title"}).find("h4").text[1:] if userDiv.find(
            "div", {"class": "user__title"}).find("h4") else None
        List = userDiv.find("ul").find_all("li")
        numberOfPosts, followers, following = ''.join(re.findall(r'\d+', List[0].text)), ''.join(
            re.findall(r'\d+', List[1].text)), ''.join(re.findall(r'\d+', List[2].text))
        description = userDiv.find("div", {"class": "user__info-desc"}).text
        user["ProfileImage"] = userImage
        user["Title"] = userTitle
        user["Username"] = userName
        user["TotalPosts"] = numberOfPosts
        user["Followers"] = followers
        user["Following"] = following
        user["Desc"] = description
        user["stories"] = BuildStories(soup, userName)
    return user


async def GetData(username, userId=None, cursor=None, token=None):
    data = {}
    if cursor:
        response = requests.get(BuildNextUrl(
            userId, cursor, token), headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
    else:
        response = requests.get(
            'https://dumpor.com/v/'+username, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        data["UserData"] = GetUserData(soup)
    data["has_next_page"] = False
    data["next_url"] = GetNextUrl(userId, soup)
    if data["next_url"]:
        data["has_next_page"] = True
    data["posts"] = await ExtractProfilePosts(soup)
    return data
