import logging
import os
import re
import datetime
import requests
from dotenv import load_dotenv

#from requests.exceptions import RequestException

from .wprescueExportAndImport import ExportAndImport
from .wprescueAfterImport import AfterImport

load_dotenv(".env")
ORIGIN_API = os.environ["ORIGIN_API"]
#DESTINATION_API = os.environ["DESTINATION_API"]
#BOT_NAME = os.environ["BOT_NAME"]
#BOT_PASSWORD = os.environ["BOT_PASSWORD"]

def purge(page: str):
    url=f"{ORIGIN_API}?action=purge&format=json&formatversion=2&titles={page}"
    r = requests.post(url).json()

def getsource(page: str):
    url=f"{ORIGIN_API}?action=query&format=json&prop=revisions&formatversion=2&rvprop=content&rvslots=main&titles={page}"
    r = requests.get(url).json()['query']['pages'][0]['revisions'][0]['slots']['main']['content']
    return r

def main():
    jst = datetime.timezone(datetime.timedelta(hours=9),'JST')
    #afd=datetime.datetime.now().strftime('Wikipedia:削除依頼/ログ/%Y年%-m月%-d日')
    afd='Wikipedia:削除依頼/ログ/2024年3月23日' #for developing on windows
    purge(afd)
    afdsource=getsource(afd)
    afdrequests = re.findall(r'\{\{(Wikipedia.*?)\}\}', afdsource)
    articles = []
    for i in afdrequests:
        page=re.findall(r'\{\{Page\|(.*?)\}\}',getsource(i))
        articles+=page
    for i in articles:
        ExportAndImport(title=i)
        AfterImport(i)

if __name__ == "__main__":
    main()