import pymysql
import requests
from bs4 import BeautifulSoup
import json
import re
import sys
import time
import random
import pandas as pd

con = pymysql.connect(host='localhost',
                     user='crawl',
                     passwd='crawlpw',
                     db='crawl_data')
cur = con.cursor()

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}

def get_news(n_url):
    news_detail = []
    print(n_url)
    breq = requests.get(n_url, headers=header)
    bsoup = BeautifulSoup(breq.content, 'html.parser')

    title = bsoup.select('h3#articleTitle')[0].text
    news_detail.append(title)

    pdate = bsoup.select('.t11')[0].get_text()[:11]
    news_detail.append(pdate)

    _text = bsoup.select("#articleBodyContents")[0].get_text().replace('\n', " ")
    btext = _text.replace(
        "// flash 오류를 우회하기 위한 함수 추가 function_flash_removeCallback() {}", "")
    news_detail.append(btext.strip())

    pcompany = bsoup.select('#footer address')[0].a.get_text()
    news_detail.append(pcompany)

    return news_detail

columns = ['날짜', '신문사', '제목', '내용']
df = pd.DataFrame(columns=columns)

query = '코로나'
s_date = "2020.04.01"
e_date = "2020.04.08"
s_from = s_date.replace(".", "")
e_to = e_date.replace(".", "")

for q in query:
    page = 1

    while True:
        time.sleep(random.sample(range(3), 1)[0])
        print(page)

        url = "https://search.naver.com/search.naver?where=new&query=" + query + \
            "&sirt=1&field=1&ds=" + s_date + "&de=" + e_date + \
            "&nso=so%3Ar%wCp%3Afrom" + s_from + "to" + \
            e_to + "%2Ca%3A&start=" + str(page)

        req = requests.get(url, headers=header)
        print(url)
        cont = req.content
        soup = BeautifulSoup(cont, 'html.parser')

        if soup.findAll("a", {"class": "info"}) == []:
            break

        for urls in soup.findAll("a", {"class": "info"}):
            try:
                if urls.attrs["href"].startswith("https://news.naver.com"):
                    print(urls.attrs["href"])
                    news_detail = get_news(urls.attrs["href"])
                    print(news_detail)
                    df = df.append(pd.DataFrame(
                        [[news_detail[1], news_detail[3], news_detail[0], news_detail[2]]], columns=columns))

                    with con.cursor() as cur:
                        cur.execute("INSERT INTO news_articles VALUES(%s, %s, %s, %s)",
                                    (news_detail[1], news_detail[3], news_detail[0], news_detail[2]))
                        con.commit()

            except Exception as e:
                print(e)
                continue
        page +=1

con.commit()