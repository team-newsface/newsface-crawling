import requests
import csv
import re
from bs4 import BeautifulSoup
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

link_list = ['https://news.naver.com/main/main.nhn?mode=LSD&mid=shm&sid1=100', 'https://news.naver.com/main/main.nhn?mode=LSD&mid=shm&sid1=101', 'https://news.naver.com/main/main.nhn?mode=LSD&mid=shm&sid1=102',
             'https://news.naver.com/main/main.nhn?mode=LSD&mid=shm&sid1=103', 'https://news.naver.com/main/main.nhn?mode=LSD&mid=shm&sid1=104', 'https://news.naver.com/main/main.nhn?mode=LSD&mid=shm&sid1=105']

naver_news = "https://news.naver.com"

cnt = 1
url1 = ""


def requests_get(url):
    global url1
    url1 = url
    # Avoid bot blocking
    html1 = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(html1.content, "html.parser")
    if url in link_list:
        more_news(soup)
    else:
        more_news1(soup)


def more_news(soup):

    global naver_news, link_list, url1

    if url1 == link_list[0]:
        link = soup.find_all("div", {"class": "cluster_foot_inner"})
        for i in link:
            more_link = i.find("a").attrs["href"]
            real_link = naver_news + more_link
            requests_get(real_link)
    else:
        link1 = soup.find_all("div", {"class": "cluster_head_topic_wrap"})
        for i1 in link1:
            more_link1 = i1.find("a").attrs["href"]
            real_link1 = naver_news + more_link1
            requests_get(real_link1)


def more_news1(soup):
    link = soup.select("#main_content > div > ul > li > dl > dt > a")
    plink = soup.select("#main_content > div > ul > li > dl > dt.photo > a")
    for pl in plink:
        link.remove(pl)

    for l in link:
        more_link = l["href"]
        title = l.get_text()
        con_craw(more_link, title)


while True:
    def con_craw(url, title):
        global cnt
        print(cnt, " "+url)
        cnt += 1

        oid = url.split("/")[5]
        aid = url.split("/")[6].split("?")[0]

        page = 1
        header = {
            "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36", "referer": url, }

        while True:

            c_url = "https://apis.naver.com/commentBox/cbox/web_neo_list_jsonp.json?ticket=news&templateId=default_society&pool=cbox5&_callback=jQuery1707138182064460843_1523512042464&lang=ko&country=&objectId=news" + \
                oid + "%2C" + aid + "&categoryId=&pageSize=20&indexSize=10&groupId=&listType=OBJECT&pageType=more&page=" + \
                    str(page) + "&refresh=false&sort=FAVORITE"
            r = requests.get(c_url, headers=header)

            html = BeautifulSoup(r.content, "html.parser")

            total_comm = str(html).split('comment":')[1].split(",")[0]

            time = re.findall('"modTime":([^\*]*),"modTimeGmt"', str(html))
            name = re.findall('"userName":([^\*]*)[*]{4}"', str(html))
            cont = re.findall('"contents":([^\*]*),"userIdNo"', str(html))
            symp = re.findall(
                '"sympathyCount":([^\*]*),"antipathyCount"', str(html))
            anti = re.findall(
                '"antipathyCount":([^\*]*),"hideReplyButton"', str(html))

            for a, b, c, d, e in zip(time, name, cont, symp, anti):
                c = re.sub('[^\w\s]', '', c)
                c = re.sub('([ㄱ-ㅎㅏ-ㅣ]+)', '', c)
                c = re.sub('ㆍ', '', c)
                c = re.sub('n', '', c)
                c = re.sub('ᆢ', '', c)
                with open("title.csv", "a", newline="")as f:
                    wr = csv.writer(f)
                    wr.writerow([title.replace('"', ''),
                                 url,
                                 a.replace("+0900", "").replace("T",
                                                                " ").replace('"', ''),
                                 b.replace('"', ''),
                                 c.replace('"', ''),
                                 d,
                                 e])

            if int(total_comm) <= ((page) * 20):
                break
            else:
                page += 1

    def wcsv():
        with open("title.csv", "w")as f:
            wr = csv.writer(f)
            wr.writerow(["Title", "URL", "Time", "ID",
                        "Comments", "S ympathy", "Antipathy"])

        for i in link_list:
            requests_get(i)

    if __name__ == '__main__':
        wcsv()
