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

def exportxml(titlee,fid: str):
    xmlurl=f"{ORIGIN_SCRIPT}?title=Special:Export&action=submit&history=1&pages={titlee}"
    wget.download(xmlurl,fid)

def importxmlandedit(title,titlee,fid: str, altname: str = ""):
    importsummary=f"ボットによる自動インポート: ウィキペディア日本語版 [[jawp:{title}|https://ja.wikipedia.org/wiki/{title}]] から全版をインポートしました"
    editsummary="ボットによる自動編集: インポート後の処理"
    if altname:
        movereason=f"ボットによる自動移動: 既に「[[{title}]]」が存在するため、代替ページ名で保存しました"
        prefix="Project:Temp"
        title = prefix+"/"+title
        titlee = prefix+"/"+titlee
    S = requests.Session()
    logintoken = S.get(url=DESTINATION_API, params={"action": "query","meta": "tokens","type": "login","format": "json"}).json()['query']['tokens']['logintoken']
    R = S.post(DESTINATION_API, data={"action":"login","lgname":BOT_NAME,"lgpassword":BOT_PASSWORD,"format":"json","lgtoken":logintoken})
    print(R)
    csrftoken = S.get(url=DESTINATION_API, params={"action": "query","meta": "tokens","format": "json"}).json()['query']['tokens']['csrftoken']
    #### import
    file={'xml':(fid, open(os.path.abspath(fid)))} #with filepath
    if altname:
        R = S.post(url=DESTINATION_API, files=file, data={"action": "import","summary": importsummary,"format": "json","token": csrftoken,"interwikiprefix": "jawp","rootpage": prefix}).json()
    else:
        R = S.post(url=DESTINATION_API, files=file, data={"action": "import","summary": importsummary,"format": "json","token": csrftoken,"interwikiprefix": "jawp"}).json()
    print(R)
    #### edit
    url=f"{DESTINATION_API}?action=query&format=json&prop=revisions&formatversion=2&rvprop=content&rvslots=main&titles={titlee}"
    source = requests.get(url).json()['query']['pages'][0]['revisions'][0]['slots']['main']['content']
    edited=re.sub('\<\!\-\-\s削除について[\s\S]*?(.*)しないでください。\s\-\-\>', '{{AutoImported|v1|app=v8|y={{subst:CURRENTYEAR}}|m={{subst:CURRENTMONTH}}|d={{subst:CURRENTDAY2}}}}', source)
    R = S.post(url=DESTINATION_API, data={"action": "edit","title": title,"summary": editsummary,"format": "json","token": csrftoken,"text": edited}).json()
    print(R)
    ### move
    if altname:
        R = S.post(url=DESTINATION_API, data={"action": "move","from": title,"to": altname,"reason": movereason,"noredirect": "1","ignorewarnings": "1","format": "json","token": csrftoken}).json()
        print(R)

def ExportAndImport(title: str, altname: str = ""):
    fid = str(int(time.time()))+".xml" #unique filename
    titlee = urllib.parse.quote(title) #encode
    exportxml(titlee=titlee,fid=fid)
    importxmlandedit(title=title,titlee=titlee,altname=altname,fid=fid)
