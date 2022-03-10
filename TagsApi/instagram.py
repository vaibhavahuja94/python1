import requests
from bs4 import BeautifulSoup
import re
import json
import timeago
import datetime
import asyncio
import aiohttp
import config
import base64
import urllib.parse
import TagsApi.picuki as picuki
##


def shortcode_to_id(shortcode):
    code = ('A' * (12-len(shortcode)))+shortcode
    return int.from_bytes(base64.b64decode(code.encode(), b'-_'), 'big')


def EncodeUrl(url):
    return base64.urlsafe_b64encode(bytes(url, 'utf-8')).decode("UTF-8")


def GetDateFromTimestamp(timestamp):
    date = datetime.datetime.fromtimestamp(timestamp)
    return timeago.format(date, datetime.datetime.now())


def GetDataFromSections(sections):
    posts = []
    for section in sections:
        medias = section["layout_content"]["medias"]
        for media in medias:
            post = {}
            post["media_id"] = shortcode_to_id(media["media"]["code"])
            post["content"] = media["media"]["caption"]["text"]
            post["likes"] = media["media"]["like_count"]
            post["comments"] = media["media"]["comment_count"]
            post["date"] = GetDateFromTimestamp(media["media"]["taken_at"])
            post["medias"] = []
            if "image_versions2" in media["media"].keys():
                post["post_type"] = "image"
                post["medias"].append(
                    {"url": "https://my-proxy0.herokuapp.com/cdn?url=" + EncodeUrl(media["media"]["image_versions2"]["candidates"][0]["url"]), "type": "image"})
                if "video_versions" in media["media"].keys():
                    post["post_type"] = "video"
                    post["medias"].append(
                        {"url": "https://my-proxy0.herokuapp.com/cdn?url=" + EncodeUrl(media["media"]["video_versions"][0]["url"]), "type": "video"})
            else:

                post["post_type"] = "image" if media["media"]["carousel_media"][0]["media_type"] == 1 else "video"
                for carousel in media["media"]["carousel_media"]:
                    if carousel["media_type"] == 1:
                        post["medias"].append(
                            {"url": "https://my-proxy0.herokuapp.com/cdn?url=" + EncodeUrl(carousel["image_versions2"]["candidates"][0]["url"]), "type": "image"})
                    else:
                        post["medias"].append(
                            {"url": "https://my-proxy0.herokuapp.com/cdn?url=" + EncodeUrl(carousel["video_versions"][0]["url"]), "type": "video"})
            posts.append(post)
    return posts


def BuildNextInstUrl(tag, cursor, token):
    return "/api/tags/{}/?cursor={}&token={}".format(tag, cursor, token)


def GetNextInsReq(tag, cursor, token):
    cookies = {
        'fbm_124024574287414': 'base_domain=.instagram.com',
        'shbid': '342\\0548433604803\\0541676118250:01f71647da8d1e03ea9ec943af6ed11cb05d3011b9bbe63e0f27c1bc141197b595498a37',
        'shbts': '1644582250\\0548433604803\\0541676118250:01f799dee64271b17f5d4afbf0e9f764e05433940bd0bf76f853ef5a1567bd5c002ef566',
        'datr': 'YzOlYRowIcPehWoy8k7zFt9_',
        'sessionid': config.ReadSessionId(),
        'ds_user_id': '8433604803',
        'csrftoken': token,
        'rur': 'FRC\\0548433604803\\0541676150460:01f757150f7c1b203cfbdf5b5faed03d93938ede798c84628893cc9d0aa1846ea4f02a57',
        'fbsr_124024574287414': 'Gy7-EWI1W81lzRQv64aQt1NEAziGkDA490NIjuHXTQ0.eyJ1c2VyX2lkIjoiMTAwMDE5MDUxMjY4NjI3IiwiY29kZSI6IkFRQW0wWi01VThMdlRqRUo0WVgtVTY1TXFJMXU0V09tMWpmZTBnemtvS3YyajAtTmxNbDJoNWdUOVdOQkx5eDlmQlNoM0pxNE5Ma1QzUEh5YjdueVpVMEg4MEhpTkNLNHVnSC1fa3JlcnNvbDNyYUpWVTgxdV92UTJuYkVZdXVDY2pJTjNKOVA3Zy1ic3VLWXF4WkN5SHF4SzAwTkx4QXBoVDRNc2xseEZQd0ZKTGR3SkFlLTBsMTB4TnFXcS1nWnM3M2tMeTlMdWxxYngwWEt0ak9uaGRaM01na3NnS1FiRDVXSFpTeWJybVEzTzczTWpoNkpoNHMxQkV6a2RZZkh6RkpFOGNabmFMLTRzQnFYblJDbjQtT1BYbW1qcEdtT2F0eW1vMC1aNXRzeWJYeVIwNmtrNzJJUlRxOVdKLWRVYm9JMXB2dGFMdFlCUGZnN3ZIUUtJNXJFIiwib2F1dGhfdG9rZW4iOiJFQUFCd3pMaXhuallCQUt4U3pJTDREakRpOThOOUo0RGMyTkpiTXBPVGZBTTFPMGFqSm9IMGR6WkFsMlVHNERvclhDcW56R3FoUm9yZ2gzaTRqVUxRaXc5d1hIOFBYdG1qRURHTHVDVU9DbkhKYURoMmNFS0I3UzNBSzF4UWM2aU1ud2ZBb2tHOXJIWW1TZHBaQUlEWWIxUlNPVVk0ZWV4QnM4WFR0S0NianVUZlM5Smt1RCIsImFsZ29yaXRobSI6IkhNQUMtU0hBMjU2IiwiaXNzdWVkX2F0IjoxNjQ0NjE0NDA5fQ',
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'X-CSRFToken': token,
        'X-Instagram-AJAX': 'dbbaa1312a79',
        'X-IG-App-ID': '936619743392459',
        'X-ASBD-ID': '198387',
        'X-IG-WWW-Claim': 'hmac.AR3R2rsxtx3rieOJKNLtHb21LQYxl1b_1INMkI6_wvvWtg7G',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://www.instagram.com',
        'Connection': 'keep-alive',
        'Referer': 'https://www.instagram.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'AlexaToolbar-ALX_NS_PH': 'AlexaToolbar/alx-4.0.2',
        'TE': 'trailers',
    }

    data = [
        ('include_persistent', '0'),
        ('max_id', cursor),
        ('surface', 'grid'),
        ('tab', 'recent'),
    ]
    return requests.post("https://i.instagram.com/api/v1/tags/{}/sections/".format(tag), data=data, headers=headers, cookies=cookies)


def GetInstaData(tag, cursor="", token="", nextMedias=[]):
    posts = []
    data = {}
    if cursor:
        res = GetNextInsReq(tag, cursor, token)
        posts = GetDataFromSections(res.json()["sections"])
        data["has_next_page"] = res.json()["more_available"]
        if data['has_next_page']:
            next_cursor = res.json()['next_max_id']
            data["next_url"] = BuildNextInstUrl(
                tag, next_cursor, token)

    else:
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

        cookies = {
            'sessionid': config.ReadSessionId(),
            'ds_user_id': '8433604803',
            'csrftoken': 'wvw8iMJgzUXvi4M2oL6lsQoBf5nNN6O5',
            'rur': 'FRC\\0548433604803\\0541676126767:01f72623905d4631da110a67a9c2c381d5af19e53ef891fa7dc4b409c607df301835df62',
            'fbsr_124024574287414': 'FInUSVLZnJ-R0ysPQnnqrAAUrWBvFafKH2zAf4p4Zy8.eyJ1c2VyX2lkIjoiMTAwMDE5MDUxMjY4NjI3IiwiY29kZSI6IkFRRG9qWXNkYldyam9EbDlZNmlMZjJ4RVhVWGRSa29Fd1l5U2lTMHI4LTVJLU1DbThab29Fcl9VZVc1eWk5blc1dEo4d1V1MWY4eGxFQ2RUYjc4WDVZYnBuQkJ3VVRhTHZ4cjFGTFNDN3o4dmppX3BaX3E1MDZzWFBCalh1UDZFMU9fdzZhRTUwT0g1MkNmLVF0YWZzcXVWRzJlMVRxSXdyTUxtd05DbG16WlRfSllWMVBTOVlaNTJuQVJlc0FFdUZhZFJxS28yRkFvQ2psbFZJcldoeTNkbE1fc3JxTGkyWjFDY042NG9hVXpaMGMwQkFHb183OFlBWVgzVTN0TkFsV0J3REF5OUtZLTFJUWVLWWI2LS1aS0lienFiVE10ckFOa3dGQnJ1ekFTb2RoNHlKc1E2akdwMFZnV095bkdZUGd3SHJDOTJ5NVFTYkJnbmd4UGU4Tmx0Iiwib2F1dGhfdG9rZW4iOiJFQUFCd3pMaXhuallCQUJkMjdLd1E5cmR5Mkpuajc5dkNESjZvYWEwMnhOYzFwRnVrT25CWW85QWI1eHBaQXVrbExaQ3hXYmdMWkNaQnBZYUZyWkFkY04wTkU0UVkxRFdaQ1pCM3poWTV1ZU9WeDdzbTNUTnRDZHJtdXdzVnBJa2hMWkN5Z2VnMVpDNElWTXhvSjZJUHpvSXpBZzVTVnlVU081Skl5SE5ubXJMTFhnb0p0U1ZzZGVNTlpDIiwiYWxnb3JpdGhtIjoiSE1BQy1TSEEyNTYiLCJpc3N1ZWRfYXQiOjE2NDQ1OTE1MDB9',
        }

        res = requests.get(
            'https://www.instagram.com/explore/tags/{}/'.format(tag), headers=headers, cookies=cookies)

        if len(re.findall(r'window._sharedData.*?=\s*(.*?)};', res.text, re.DOTALL | re.MULTILINE)) != 0:
            jsonData = json.loads(re.findall(
                r'window._sharedData.*?=\s*(.*?)};', res.text, re.DOTALL | re.MULTILINE)[0]+"}")
            data['token'] = jsonData['config']["csrf_token"]

        RecentData = jsonData["entry_data"]["TagPage"][0]["data"]["recent"]
        posts = GetDataFromSections(RecentData["sections"])
        data["has_next_page"] = RecentData["more_available"]

        if data['has_next_page']:
            next_cursor = RecentData['next_max_id']
            data["next_url"] = BuildNextInstUrl(
                tag, next_cursor, data['token'])

            #data = asyncio.run(GetData(tag, cursor, token))
            #data = picuki.getTagsDataFromPicuki(tag, cursor, token)

    data["posts"] = posts
    return data
