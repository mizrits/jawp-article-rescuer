import os
import re
import time
import datetime
import requests
from dotenv import load_dotenv
import urllib.parse
#from requests.exceptions import RequestException
from .wprescueExportAndImport import ExportAndImport

load_dotenv(".env")
ORIGIN_API = os.environ["ORIGIN_API"]
DESTINATION_API = os.environ["DESTINATION_API"]
BOT_NAME = os.environ["BOT_NAME"]
BOT_PASSWORD = os.environ["BOT_PASSWORD"]

jst = datetime.timezone(datetime.timedelta(hours=9),'JST')
log="== ~~~~~ ==\n"

def logging(msg):
    global log
    event=f"{datetime.datetime.now(jst).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]} {msg}"
    log+=f" {event}\n"
    return event

def savelog(log: str):
    S = requests.Session()
    logintoken = S.get(url=DESTINATION_API, params={"action": "query","meta": "tokens","type": "login","format": "json"}).json()['query']['tokens']['logintoken']
    R = S.post(DESTINATION_API, data={"action":"login","lgname":BOT_NAME,"lgpassword":BOT_PASSWORD,"format":"json","lgtoken":logintoken})
    print(R)
    csrftoken = S.get(url=DESTINATION_API, params={"action": "query","meta": "tokens","format": "json"}).json()['query']['tokens']['csrftoken']
    summary="ボットによる自動記録: 作動ログの保存"
    title=datetime.datetime.now(jst).strftime('Project:ArchiverBot/Log/%Y%m%d')
    R = S.post(url=DESTINATION_API, data={"action": "edit","title": title,"summary": summary,"format": "json","token": csrftoken,"appendtext": log}).json()
    print(R)

def purge(page: str):
    pagee=urllib.parse.quote(page)
    url=f"{ORIGIN_API}?action=purge&format=json&formatversion=2&titles={pagee}"
    r = requests.post(url).json()
    return r

def getsource(page: str):
    pagee=urllib.parse.quote(page)
    url=f"{ORIGIN_API}?action=query&format=json&prop=revisions&formatversion=2&rvprop=content&rvslots=main&titles={pagee}"
    r = requests.get(url).json()['query']['pages'][0]['revisions'][0]['slots']['main']['content']
    return r

def getinfo(list: list, type: str):
    input = urllib.parse.quote('|'.join(list))
    url=f"{ORIGIN_API}?action=query&format=json&prop=info&formatversion=2&{type}={input}"
    r = requests.get(url).json()['query']['pages']
    return r

def main():
    start = time.perf_counter()
    afd=datetime.datetime.now().strftime('Wikipedia:削除依頼/ログ/%Y年%-m月%-d日')
    #afd='Wikipedia:削除依頼/ログ/2024年3月23日' #for developing on windows
    purge(afd)
    afdsource=getsource(afd)

    print(logging(f"[[jawp:{afd}]] を読み込みました"))
    afdrequests = re.findall(r'\{\{(Wikipedia.*?)\}\}', afdsource)
    print(logging(f"{len(afdrequests)}件 の削除依頼が提出されています"))

    print(logging(f"特記号付きの依頼を除外しています"))
    afdrequestsforurl = '|'.join(afdrequests)
    url=f"{ORIGIN_API}?action=query&format=json&prop=revisions&formatversion=2&rvprop=content&rvslots=main&titles="+afdrequestsforurl
    r = requests.get(url).json()['query']['pages']
    articlenames=[]
    articleids=[]
    markedrequests=0
    for i in range(0,len(afdrequests)):
        content=r[i]['revisions'][0]['slots']['main']['content']
        if not re.match(r'===\s*(\([緊特\*]{1,3}\).*?)\s*===',content):
            articlenames+=re.findall(r'\{\{Page\|(.*?)\}\}',content)
            articleids+=re.findall(r'\{\{Page\/ID\|(.*?)\}\}',content)
        else:
            markedrequests+=1
    print(logging(f"特記号付きの依頼 {markedrequests}件 は除外されました。"))
    print(logging(f"残りの {len(afdrequests)-markedrequests}件 の依頼から、 {len(articlenames)}本 のページ名、 {len(articleids)}本 のページIDが見つかりました"))

    articlesbyid=[]
    if articleids:
        print(logging(f"ページIDの解析: IDから存在している標準名前空間のページを探しています…"))
        info=getinfo(list=articleids, type="pageids")
        for i in range(0,len(articleids)):
            title=info[i]['title']
            try:
                if info[i]['ns'] == 0:
                    print(logging(f"◆「{title}」…OK"))
                    articlesbyid+=[title]
                else:
                    print(logging(f"◆「{title}」…名前空間が異なるため除外"))
            except KeyError:
                print(logging(f"◆「{title}」…既にページが存在しません"))
        print(logging(f"{len(articlesbyid)}本 見つかりました"))

    articlesbyname=[]
    if articlenames:
        print(logging(f"ページ名の解析: 存在している標準名前空間のページを探しています"))
        info=getinfo(list=articlenames, type="titles")
        for i in range(0,len(articlenames)):
            title=info[i]['title']
            try:
                existence=info[i]['length']
                if info[i]['ns'] == 0:
                    print(logging(f"◆「{title}」…OK"))
                    articlesbyname+=[title]
                else:
                    print(logging(f"◆「{title}」…名前空間が異なるため除外"))
            except KeyError:
                print(logging(f"◆「{title}」…既にページが存在しません"))
        print(logging(f"{len(articlesbyname)}本 見つかりました"))

    articles=list(set(articlesbyid+articlesbyname))
    print(logging(f"重複を除き、合計 {len(articles)}本 の記事を確認しました: {articles}"))

    for i in articles:
        print(logging(f"{i} をエクスポート・インポートしています…"))
        ExportAndImport(i)
        print(logging(f"{i} の移入が完了しました"))

    end = time.perf_counter()
    print(logging(f"全ての処理を完了しました。経過時間:{end-start:.4f}秒"))
    savelog(log)


if __name__ == "__main__":
    main()
