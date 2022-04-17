from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from jinja2 import Template


token = "token.json"
sheet = "Sitemap"
maxUrlsPerFile = 200000
sitemap_template = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    {% for page in pages %}
    <url>
        <loc>{{page[0]|safe}}</loc>
        <lastmod>{{page[1]}}</lastmod>
        <changefreq>{{page[2]}}</changefreq>
        <priority>{{page[3]}}</priority>        
    </url>
    {% endfor %}
</urlset>'''

template = Template(sitemap_template)


def initGspreadClient():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        token, scope)
    client = gspread.authorize(creds)
    return client


def getTargets(Urls):
    Urls = Urls
    pages = []
    page = 1
    while True:
        if len(Urls) > maxUrlsPerFile*(page-1):
            if len(Urls) > maxUrlsPerFile*(page):
                pages.append(
                    Urls[maxUrlsPerFile*(page-1):maxUrlsPerFile*(page)])
            else:
                pages.append(Urls[maxUrlsPerFile*(page-1):])
        else:
            break
        page += 1
    return pages


def UpdateSitemap():
    cl = initGspreadClient()
    MainSheet = cl.open(sheet).worksheet("Urls")
    #
    Urls = MainSheet.col_values(1)[1:]
    #
    last_mod = datetime.datetime.now().strftime('%Y-%m-%d')
    #
    changefreq = "daily"
    #
    priority = "1"
    #
    print("Updating Sitemaps///")
    #
    for i, p in enumerate(getTargets(Urls)):
        pages = []
        for U in p:
            page = []
            page.append(U)
            page.append(last_mod)
            page.append(changefreq)
            page.append(priority)
            pages.append(page)
        file_content = template.render(pages=pages)
        with open("Sitemaps/sitemap{}.xml".format(i+1), "w+") as f:
            f.write(file_content)
    print("done")
