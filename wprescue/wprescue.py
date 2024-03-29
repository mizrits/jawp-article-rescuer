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
jst = datetime.timezone(datetime.timedelta(hours=9),'JST')

def jstime():
    return datetime.datetime.now(jst).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]

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

def main():
    start = time.perf_counter()
    #削除依頼ログにアクセスし、ソースを取得
    afd=datetime.datetime.now().strftime('Wikipedia:削除依頼/ログ/%Y年%-m月%-d日')
    #afd='Wikipedia:削除依頼/ログ/2024年3月23日' #for developing on windows
    purge(afd)
    afdsource=getsource(afd)
    print(f"{jstime()} {afd} を読み込みました")
    afdrequests = re.findall(r'\{\{(Wikipedia.*?)\}\}', afdsource)
    print(f"{jstime()} {len(afdrequests)}件 の削除依頼が見つかりました")
    afdrequestsforurl = '|'.join(afdrequests)
    url="https://ja.wikipedia.org/w/api.php?action=query&format=json&prop=revisions&formatversion=2&rvprop=content&rvslots=main&titles="+afdrequestsforurl
    r = requests.get(url).json()
    articlenames=[]
    articleids=[]
    print(f"{jstime()} 特記号付きの依頼を除外しています")
    for i in range(0,len(afdrequests)):
    title=r['query']['pages'][i]['title']
    content=r['query']['pages'][i]['revisions'][0]['slots']['main']['content']
    if not re.match(r'===\s*(\([緊特\*]{1,3}\).*?)\s*===',content):
        articlenames+=re.findall(r'\{\{Page\|(.*?)\}\}',content)
        articleids+=re.findall(r'\{\{Page\/ID\|(.*?)\}\}',content)
    print(f"{jstime()} {len(articlenames)}件 のページ名、 {len(articleids)}件 のページIDが見つかりました")

    articlesbyid=[]
    if articleids:
        print(f"{jstime()} ページIDの解析を行います…")
        articleidsforurl = '|'.join(articleids)
        url="https://ja.wikipedia.org/w/api.php?action=query&format=json&prop=info&formatversion=2&pageids="+articleidsforurl
        r = requests.get(url).json()

        print(f"{jstime()} IDから存在している標準名前空間のページを探しています")
        for i in range(0,len(articleids)):
            try:
                if r['query']['pages'][i]['ns'] == 0:
                    print(f"{jstime()} ◆「{r['query']['pages'][i]['title']}」…OK")
                    articlesbyid+=[r['query']['pages'][i]['title']]
                else:
                    print(f"{jstime()} ◆「{r['query']['pages'][i]['title']}」…名前空間が異なるため除外")
            except KeyError:
                print(f"{jstime()} ◆「{r['query']['pages'][i]['title']}」…既にページが存在しません")
        print(f"{jstime()} {len(articlesbyid)}件 見つかりました")
    
    articlesbyname=[]
    if articlenames:
        print(f"{jstime()} ページ名の解析を行います…")
        articlenamesforurl = '|'.join(articlenames)
        url="https://ja.wikipedia.org/w/api.php?action=query&format=json&prop=info&formatversion=2&titles="+urllib.parse.quote(articlenamesforurl)
        r = requests.get(url).json()
        print(f"{jstime()} 存在している標準名前空間のページを探しています")
        for i in range(0,len(articlenames)):
            try:
                existence=r['query']['pages'][i]['length']
                if r['query']['pages'][i]['ns'] == 0:
                    print(f"{jstime()} ◆「{r['query']['pages'][i]['title']}」…OK")
                    articlesbyname+=[r['query']['pages'][i]['title']]
                else:
                    print(f"{jstime()} ◆「{r['query']['pages'][i]['title']}」…名前空間が異なるため除外")
            except KeyError:
                print(f"{jstime()} ◆「{r['query']['pages'][i]['title']}」…既にページが存在しません")
        print(f"{jstime()} {len(articlesbyname)}件 見つかりました")
    
    articles=list(set(articlesbyid+articlesbyname))
    print(f"{jstime()} 合計 {len(articles)}件 の記事を確認しました: {articles}")

    for i in articles:
        ExportAndImport(title=i)

end = time.perf_counter()
print(jstime()+" 全ての処理を完了しました。経過時間:{:.4f}".format(end-start))



if __name__ == "__main__":
    main()
