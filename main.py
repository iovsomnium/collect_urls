import requests
from bs4 import BeautifulSoup
import re

class NewsCrawler:
    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/98.0.4758.102"}
        self.news_data = []

    def makePgNum(self, num):
        if num == 1:
            return num
        elif num == 0:
            return num+1
        else:
            return num+9*(num-1)

    def make_url(self, search, start_date, end_date):
        urls = []
        for i in range(1, 401):
            page = self.make_pg_num(i)
            url = "https://search.naver.com/search.naver?where=news&sm=tab_pge&query=" + search + "&sort=2&photo=0&field=0&pd=3&ds="+start_date+"&de="+end_date+"&start=" + str(page)
            urls.append(url)
        return urls

    def news_attrs_crawler(self, articles, attrs):
        attrs_content = []
        for i in articles:
            attrs_content.append(i.attrs[attrs])
        return attrs_content

    def articles_crawler(self, url):
        original_html = requests.get(url, headers=self.headers)
        html = BeautifulSoup(original_html.text, "html.parser")
        url_naver = html.select("div.group_news > ul.list_news > li div.news_area > div.news_info > div.info_group > a.info")
        url = self.news_attrs_crawler(url_naver, 'href')
        return url
    
    def makeList(self, newlist, content):
        for i in content:
            for j in i:
                newlist.append(j)
        return newlist

    def crawl_news_urls(self, search, start_date, end_date, filename):
        # URL 생성
        urls = self.make_url(search, start_date, end_date)

        # 기사 URL 수집
        news_urls = []
        for url in urls:
            urls = self.articles_crawler(url)
            news_urls.extend(urls)

        # 중복 제거 및 "news.naver.com"을 포함하는 URL 필터링
        final_urls = [url for url in news_urls if "news.naver.com" in url]

        # 텍스트 파일에 누적 저장
        with open(filename, "a", encoding="utf-8") as file:
            for url in final_urls:
                file.write(url + "\n")

        # 저장된 URL 목록 반환
        return final_urls
    
    
    def get_last_news_date(self, filename):
        # 텍스트 파일에서 마지막 URL 가져오기
        with open(filename, "r", encoding="utf-8") as file:
            lines = file.readlines()
            last_url = lines[-1].strip()

        # URL로부터 뉴스 날짜 추출
        html = requests.get(last_url, headers=self.headers)
        soup = BeautifulSoup(html.text, "html.parser")
        pattern1 = '<[^>]*>'

        try:
            html_date = soup.select_one("div#ct> div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_info_datestamp > div > span")
            news_date = html_date.attrs['data-date-time']
        except AttributeError:
            news_date = soup.select_one("#content > div.end_ct > div > div.article_info > span > em")
            news_date = re.sub(pattern=pattern1, repl='', string=str(news_date))

        print(html_date)
        news_date = html_date.attrs['data-date-time']
        
        return news_date

# 사용 예시
crawler = NewsCrawler()

# 검색어와 페이지 범위 설정
search = "삼성전자"
start_pg = "2023.01.01"
end_pg = "2023.01.06"

# 텍스트 파일명 설정
filename = "news_urls.txt"

# 뉴스 URL 크롤링 및 저장
news_urls = crawler.crawl_news_urls(search, start_pg, end_pg, filename)

last_news_date = crawler.get_last_news_date(filename)
print(last_news_date)
