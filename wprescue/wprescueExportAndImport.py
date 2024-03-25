import logging
import os
import sys
import wget
import time
import requests
from dotenv import load_dotenv

#from requests.exceptions import RequestException

load_dotenv(".env")
#ORIGIN_API = os.environ["ORIGIN_API"]
ORIGIN_SCRIPT = os.environ["ORIGIN_SCRIPT"]
DESTINATION_API = os.environ["DESTINATION_API"]
BOT_NAME = os.environ["BOT_NAME"]
BOT_PASSWORD = os.environ["BOT_PASSWORD"]

def exportxml(title,fid: str):
    xmlurl="https://ja.wikipedia.org/w/index.php?title=Special:Export&action=submit&history=1&pages="+urllib.parse.quote(title)
    wget.download(xmlurl,fid)

def importxml(title,fid: str):
    S = requests.Session()
    logintoken = S.get(url=DESTINATION_API, params={"action": "query","meta": "tokens","type": "login","format": "json"}).json()['query']['tokens']['logintoken']
    R = S.post(DESTINATION_API, data={"action":"login","lgname":BOT_NAME,"lgpassword":BOT_PASSWORD,"format":"json","lgtoken":logintoken})
    print(R)
    csrftoken = S.get(url=DESTINATION_API, params={"action": "query","meta": "tokens","format": "json"}).json()['query']['tokens']['csrftoken']
    summary=f"ボットによる自動インポート: ウィキペディア日本語版 https://ja.wikipedia.org/wiki/{title} から全版をインポートしました"
    file={'xml':(fid, open(os.path.abspath(fid)))} #with filepath
    R = S.post(url=DESTINATION_API, files=file, data={"action": "import","summary": summary,"format": "json","token": csrftoken,"interwikiprefix": "jawp"}).json()
    print(R)

def ExportAndImport(title):
    fid = str(int(time.time()))+".xml" #unique filename
    exportxml(title=title,fid=fid)
    importxml(title=title,fid=fid)


if __name__ == "__main__":
    sys.exit(ExportAndImport()) 