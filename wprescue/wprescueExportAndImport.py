import urllib.parse
import os
import re
import sys
import wget
import time
import requests
from dotenv import load_dotenv
#from requests.exceptions import RequestException

load_dotenv(".env")
ORIGIN_SCRIPT = os.environ["ORIGIN_SCRIPT"]
DESTINATION_API = os.environ["DESTINATION_API"]
BOT_NAME = os.environ["BOT_NAME"]
BOT_PASSWORD = os.environ["BOT_PASSWORD"]

def exportxml(title,fid: str):
    xmlurl=ORIGIN_SCRIPT+"?title=Special:Export&action=submit&history=1&pages="+urllib.parse.quote(title)
    wget.download(xmlurl,fid)

def importxmlandedit(title,fid: str):
    S = requests.Session()
    logintoken = S.get(url=DESTINATION_API, params={"action": "query","meta": "tokens","type": "login","format": "json"}).json()['query']['tokens']['logintoken']
    R = S.post(DESTINATION_API, data={"action":"login","lgname":BOT_NAME,"lgpassword":BOT_PASSWORD,"format":"json","lgtoken":logintoken})
    print(R)
    csrftoken = S.get(url=DESTINATION_API, params={"action": "query","meta": "tokens","format": "json"}).json()['query']['tokens']['csrftoken']
    #### import
    summary=f"ボットによる自動インポート: ウィキペディア日本語版 https://ja.wikipedia.org/wiki/{title} から全版をインポートしました"
    file={'xml':(fid, open(os.path.abspath(fid)))} #with filepath
    R = S.post(url=DESTINATION_API, files=file, data={"action": "import","summary": summary,"format": "json","token": csrftoken,"interwikiprefix": "jawp"}).json()
    print(R)
    #### fix
    summary=f"ボットによる自動編集: インポート後の処理"
    url=f"{DESTINATION_API}?action=query&format=json&prop=revisions&formatversion=2&rvprop=content&rvslots=main&titles={title}"
    source = requests.get(url).json()['query']['pages'][0]['revisions'][0]['slots']['main']['content']
    edited=re.sub('\<\!\-\-\s削除について[\s\S]*?(.*)しないでください。\s\-\-\>', '{{AutoImported|v1|app=v1|y={{subst:CURRENTYEAR}}|m={{subst:CURRENTMONTH}}|d={{subst:CURRENTDAY2}}}}', source)
    R = S.post(url=DESTINATION_API, data={"action": "edit","title": title,"summary": summary,"format": "json","token": csrftoken,"text": edited}).json()
    print(R)

def ExportAndImport(title):
    fid = str(int(time.time()))+".xml" #unique filename
    exportxml(title=title,fid=fid)
    importxmlandedit(title=title,fid=fid)


if __name__ == "__main__":
    ExportAndImport(str(input("title")))
