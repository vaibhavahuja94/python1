import asyncio
from fastapi import FastAPI, Form
import TagScraper
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3050",
    "http://*:*",
    "https://*:*",
    "https://invewer.com",
    "http://invewer.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/tags/{tag}")
def getInitTags(tag: str, cursor: str = "", token: str = ""):
    data = TagScraper.GetInstaData(tag, cursor, token)
    return data


@app.get("/api/dumpor/tags/{tag}")
def getInitTagss(tag: str, cursor: str = "", token: str = ""):
    data = asyncio.run(TagScraper.GetData(tag, cursor, token))
    return data
