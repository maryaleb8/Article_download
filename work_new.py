import requests
from pathlib import Path
import time
import re

import requests
from bs4 import BeautifulSoup

#используя cookie авторизуется в личном кабинете
def download_and_save(url, path):
    r = requests.get(url, headers={"cookie":""" #here are cookies
	"""})
    if r.status_code != 200:
        print(r.status_code, end=" ")
        return r.status_code
    with open(path, 'wb') as f:
        f.write(r.content)
    return None

#качает статью, создавая папки
def download_and_save_article(url, article, year, sub_year):
    folder_path = f"/home/marya/Desktop/articles/{year}/{sub_year}"
    Path(folder_path).mkdir(parents=True, exist_ok=True)
    return download_and_save(url, f"{folder_path}/{re.sub('[?.!/;:!@#$]', '', article)}.pdf")

#добыча названия статьи и айди для скачивания
def parse_article(article):
    name_article = article.find('h3', class_='hed').text
    url_article = article.find('stream-item')['data-url']
    id_article = article.find('stream-item')['data-id'].split("-")[-1]
    return name_article, f'https://hbr.org/{url_article}', f"https://hbr.org/download/subscriber/reprint/{id_article}-PDF-ENG"

#ищет на странице одного выпуска все статьи
def parse_article_list(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    articles = soup.find("stream-list").find_all('li', class_='stream-entry')
    year_subyear = soup.find('div', class_='small-6 medium-3 text-right columns pubdate white ptm')
    sub_year, year = year_subyear.text.split()
    return year, sub_year, [parse_article(a) for a in articles]

#непосредственно скачивает статьи по готовой ссылке для скачивания
def download_article_list(url):
    try:
        year, sub_year, articles = parse_article_list(url)
    except Exception:
        return
    for article in articles:
        tmp = download_and_save_article(article[-1], article[0], year, sub_year)
        if tmp is not None:
            with open("/home/marya/Desktop/articles/failed.html", 'a') as file:
                file.write(f"{tmp} {year}, {sub_year}, {article[0]}, <a href=\"{article[1]}\">{article[0]}</a> <br>\n")

#скачивает определенный год
def download_year(year):
    count_articles = 7
    def get_year_url(current):
        if current >= 2010:
            return f"https://hbr.org/archive-toc/BR{current%100}"
        elif current >= 2001:
            return f"https://hbr.org/archive-toc/BR0{current%100}"
        else:
            return f"https://hbr.org/archive-toc/3{current%100}"
    if year >= 2001 and year <= 2016:
        count_articles = 13
    for m in range(1, count_articles):
        time.sleep(0.1)
        #print(get_year_url(year) + str(m))
        if m < 10:
            yield get_year_url(year) + '0' + str(m)
        else:
            yield get_year_url(year) + str(m)

#пробегается по годам
def get_article_list_urls():
    start_year = 2015 #здесь вручную меняется диапазон скачивания
    end_year = 2017
    for current in range(start_year, end_year):
        print(current)
        yield from download_year(current)

# url = "https://hbr.org/download/subscriber/reprint/G2201A-PDF-ENG"
# url = "https://hbr.org/archive-toc/BR1001"
# article = "Finding the Right CEO"
# year = "2022"
# sub_year = "January–February"

#download_and_save_article(url, article, year, sub_year)


for article_list_url in get_article_list_urls():
    download_article_list(article_list_url)

# download_article_list(url)
# print(y, sy)
# print(*a, sep="\n")
