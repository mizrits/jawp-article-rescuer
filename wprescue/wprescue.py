import sys
from loguru import logger
logger.remove()
logger.add(sys.stderr,format="{time:YYYY-MM-DD HH:mm:ss.SSS} {level} {message}", level="DEBUG")
logger.add("out.log", rotation="500MB")
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


def purge(page: str):
    logger.debug(f"Purging {afd}...")
    url=f"{ORIGIN_API}?action=purge&format=json&formatversion=2&titles={page}"
    r = requests.post(url).json()
    logger.debug(f"Result: {r}")

def getsource(page: str):
    url=f"{ORIGIN_API}?action=query&format=json&prop=revisions&formatversion=2&rvprop=content&rvslots=main&titles={page}"
    r = requests.get(url).json()['query']['pages'][0]['revisions'][0]['slots']['main']['content']
    return r

def main():
    jst = datetime.timezone(datetime.timedelta(hours=9),'JST')
    #afd=datetime.datetime.now(jst).strftime('Wikipedia:削除依頼/ログ/%Y年%-m月%-d日')
    afd='Wikipedia:削除依頼/ログ/2024年3月23日' #for developing on windows
    logger.info(f"AfD page:{afd}")
    purge(afd)
    logger.debug(f"Fetch source of {afd}...")
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