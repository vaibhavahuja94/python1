import requests
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import base64
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'AlexaToolbar-ALX_NS_PH': 'AlexaToolbar/alx-4.0.2',
    'Cache-Control': 'max-age=0',
    'TE': 'trailers',
}

###########


def proxyIt(url):
    return "https://my-proxy0.herokuapp.com/cdn?url="+base64.urlsafe_b64encode(url.encode()).decode("utf-8")


async def GetFromSaveFrom(session, UserId):
    e = None
    stories = []
    try:
        async with session.get('https://igs.sf-converter.com/api/stories/'+UserId) as response:
            resJson = await response.json()
            for item in resJson["result"]:
                post = {}
                if "video_versions" in item.keys():
                    post["type"] = "video"
                    post["url"] = item["video_versions"][0]["url"]
                else:
                    post["type"] = "image"
                    post["url"] = proxyIt(
                        item["image_versions2"]["candidates"][0]["url"])
                stories.append(post)
    except Exception as e:
        return e
    return stories

##########


def GetDumporToken(user):
    response = requests.get(
        'https://dumpor.com/v/'+user, headers=headers,)
    sp = BeautifulSoup(response.text, "html.parser")
    token = None
    if (container := sp.find("div", {"id": "stories-container"})) != None:
        token = container.get("data-token")
    return token


async def GetStoriesFromDumpor(session, userid, username, token):
    stories = []
    if not token:
        token = GetDumporToken(username)
    if token != None:
        async with session.get('https://dumpor.com/api/profile/{}/stories?token={}'.format(userid, token)) as r:
            resContent = await r.read()
            soup = BeautifulSoup(resContent, "html.parser")
            for storyDiv in soup.find("div", {"class": "carousel-inner"}).find_all("div"):
                if storyDiv.find("video") == None:
                    Type = "image"
                else:
                    Type = "video"
                url = proxyIt(storyDiv.get("data-src"))
                stories.append({"url": url, "type": Type})
    return stories


async def GetStories(userid, username, token):
    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = []

        tasks.append(asyncio.ensure_future(
            GetFromSaveFrom(session, userid)
        ))
        stories = await asyncio.gather(*tasks)

        if len(stories) != 0:
            if type(stories[0]) != list:
                try:
                    tasks = []
                    tasks.append(asyncio.ensure_future(
                        GetStoriesFromDumpor(session, userid, username, token)))
                    stories = await asyncio.gather(*tasks)
                    print("dumpr")

                except Exception as e:
                    tasks = []
                    print(e)
                    return e
    return stories


def GetStoriesData(userid, username, token):
    strories = asyncio.run(GetStories(userid, username, token))
    if (type(strories)) != list:
        return {"msg": "error"}
    else:
        return strories
