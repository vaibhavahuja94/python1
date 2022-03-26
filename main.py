import asyncio
from fastapi import FastAPI
import TagsApi.TagScraper as TagScraper
import TagsApi.dumpor as dumpor
from fastapi.middleware.cors import CORSMiddleware
import SearchAPi
import profileApi.ProfileApi as ProfileApi
import StoriesApi
import VideoApi
app = FastAPI()
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3050",
    "http://*:*",
    "https://*.*.*",
    "https://invewer.com",
    "http://invewer.com",
    "http://www.reegram.com",
    "https://www.reegram.com",
    "http://www.smihub.com.co",
    "https://www.smihub.com.co",
    "http://13.235.239.96:8001",
    "https://www.kiyaso.com",
    "http://www.kiyaso.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/tags/{tag}/")
def getInitTags(tag: str, cursor: str = "", token: str = ""):
    data = TagScraper.getTags(tag, cursor, token)
    return data


@app.get("/api/dumpor/tags/{tag}/")
def getInitTagss(tag: str, cursor: str = "", token: str = ""):
    data = asyncio.run(dumpor.GetData(tag, cursor, token))
    return data


@app.get("/api/search")
def getSearch(query: str = ""):
    print(query)
    if query != "":
        data = SearchAPi.Search(query)
    else:
        data = {"msg": "please search for query use /api/search?query=christiano", }
    return data


@app.get("/api/profile/{username}/")
def getInitTags(username: str, cursor: str = "", token: str = ""):
    data = ProfileApi.GetProfileData(username, username, cursor, token)
    return data


@app.get("/api/stories/{userid}/{username}/")
def getStories(userid, username, token: str = ""):
    stories = StoriesApi.GetStoriesData(userid, username, token)
    return {"userid": userid, "username": username, "stories": stories}


@app.get("/api/video/{idd}")
def getInitTags(idd):
    data = {"video_link": VideoApi.getVideoLink(idd)}
    return data
