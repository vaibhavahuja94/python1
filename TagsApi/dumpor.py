import requests
from bs4 import BeautifulSoup
import asyncio
import aiohttp
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


def ExtractUrlFromDumpor(l):
    parser = urllib.parse.parse_qs(l)
    s = parser[list(parser.keys())[0]][0][::-1]
    # url=base64.decodebytes(bytes(s,"utf-8")).decode("utf-8")
    return s


def GetNextUrl(tag, soup):
    cursor = ""
    token = ""
    if LoadDiv := soup.find("div", {"id": "load_more"}):
        cursor = LoadDiv.get("data-cursor")
        token = LoadDiv.get("data-token")
        if cursor != "":
            return "/api/tags/{}/?cursor={}&token={}".format(tag, cursor, token)
        else:
            return None
    else:
        return None


def BuildNextUrl(tag, cursor, token):
    return "https://dumpor.com/api/hashtags/{}/?cursor={}&token={}".format(tag, cursor, token)


def BuildNextInstUrl(tag, cursor, token):
    return "/api/tags/{}/?cursor={}&token={}".format(tag, cursor, token)


async def getDumporVideoLink(session, idd):
    print("start", idd)
    async with session.get('https://mohsiss-proxy0.herokuapp.com/?url=https://dumpor.com/c/'+idd) as r:
        # res = requests.get('https://mohsiss-proxy0.herokuapp.com/?url=https://dumpor.com/c/'+idd, headers=headers)
        content = await r.read()
        print("done", idd)
        sp = BeautifulSoup(content, "html.parser")
        if video := sp.find("div", {"class": "video-container"}):
            return video.find("video").get("src")
        return None


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


async def GetPostsJsonFromPage(tag, soup):
    # PostsList=[]
    # if PostsC:=soup.find("div",{"class":"content__list"}):
    PostsList = soup.find_all("div", {"class": "content__item"})
    if len(PostsList) == 0:
        raise Exception("no posts")
    PostsJson = []
    async with aiohttp.ClientSession(headers=headers) as session:
        ##
        tasks = []
        for Post in PostsList:
            tasks.append(asyncio.ensure_future(ExtractPostData(session, Post)))
        for x in await asyncio.gather(*tasks):
            if x != "ad":
                PostsJson.append(x)
    return PostsJson


async def GetData(tag, cursor, token):
    if cursor:
        response = requests.get(BuildNextUrl(
            tag, cursor, token), headers=headers, timeout=6)
    else:
        response = requests.get(
            'https://dumpor.com/t/'+tag, headers=headers, timeout=6)
    soup = BeautifulSoup(response.text, "html.parser")
    data = {}
    data["has_next_page"] = False
    data["next_url"] = GetNextUrl(tag, soup)
    if data["next_url"]:
        data["has_next_page"] = True
    data["posts"] = await GetPostsJsonFromPage(tag, soup)
    return data
