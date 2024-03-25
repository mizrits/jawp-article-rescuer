import logging
import os
import sys
import time
import requests
from dotenv import load_dotenv

#from requests.exceptions import RequestException

load_dotenv(".env")
DESTINATION_API = os.environ["DESTINATION_API"]
BOT_NAME = os.environ["BOT_NAME"]
BOT_PASSWORD = os.environ["BOT_PASSWORD"]

def fixarticle(title: str):
    S = requests.Session()
    logintoken = S.get(url=DESTINATION_API, params={"action": "query","meta": "tokens","type": "login","format": "json"}).json()['query']['tokens']['logintoken']
    R = S.post(DESTINATION_API, data={"action":"login","lgname":BOT_NAME,"lgpassword":BOT_PASSWORD,"format":"json","lgtoken":logintoken})
    print(R)
    csrftoken = S.get(url=DESTINATION_API, params={"action": "query","meta": "tokens","format": "json"}).json()['query']['tokens']['csrftoken']
    summary=f"ボットによる自動編集: インポート後の処理"
    file={'xml':(fid, open(os.path.abspath(fid)))} #with filepath
    R = S.post(url=DESTINATION_API, files=file, data={"action": "import","format": "json","token": csrftoken,"interwikiprefix": "jawp"}).json()
    print(R)

def AfterImport(title):
    #fixarticle(title)
    pass


if __name__ == "__main__":
    sys.exit(AfterImport()) 