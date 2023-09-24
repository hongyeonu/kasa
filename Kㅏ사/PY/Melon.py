import selenium
from selenium import webdriver as wd
import time
import pandas as pd
from bs4 import BeautifulSoup
import requests
from itertools import repeat

# 크롬드라이버 열기
driver = wd.Chrome('C:\chromdriver_win32\chromdriver') # 크롬드라이버 경로
driver.maximize_window() # 크롬창 크기 최대

# 드라이버가 해당 url 접속
url = 'https://www.melon.com/chart/index.htm' # 멜론차트 페이지
driver.get(url)

# 차트파인더 클릭
driver.find_element_by_xpath('//*[@id="gnb_menu"]/ul[1]/li[1]/div/div/button/span').click()

# 연대선택, 연도선택, 월선택, 장르선택

# 월간차트 클릭
driver.find_element_by_xpath('//*[@id="d_chart_search"]/div/h4[2]/a').click()
time.sleep(2)

# 연대선택 2000년 클릭
driver.find_element_by_xpath('//*[@id="d_chart_search"]/div/div/div[1]/div[1]/ul/li[3]/span/label').click()
time.sleep(2)

# 연도선택 2008년 클릭
driver.find_element_by_xpath('//*[@id="d_chart_search"]/div/div/div[2]/div[1]/ul/li[2]/span/label').click()
time.sleep(2)

# 월선택 8월 클릭
driver.find_element_by_xpath('//*[@id="d_chart_search"]/div/div/div[3]/div[1]/ul/li[8]/span/label').click()
time.sleep(2)

# 장르선택 종합 클릭
driver.find_element_by_xpath('//*[@id="d_chart_search"]/div/div/div[5]/div[1]/ul/li[1]/span/label').click()
time.sleep(2)

# 검색버튼 클릭
driver.find_element_by_xpath('//*[@id="d_srch_form"]/div[2]/button/span/span').click()

html = driver.page_source # 드라이버 현재 페이지의 html 정보 가져오기 
                            # cf) requests.get(url)
soup = BeautifulSoup(html, 'lxml')

soup.find_all('div', attrs={'class': 'ellipsis rank01'})

[title.find('a').get_text() for title in soup.find_all('div', attrs={'class': 'ellipsis rank01'})]

soup.find_all('span', attrs={'class':'checkEllipsis'})

[ singer.get_text() for singer in soup.find_all('span', attrs={'class':'checkEllipsis'}) ]

soup.find_all('span', attrs={'class':'rank top'})

song = [title.find('a').get_text() for title in soup.find_all('div', attrs={'class': 'ellipsis rank01'})]
rank = []
for i in range(len(song)):
    rank.append(i+1)

soup.find_all('span', attrs={'class':'datelk'})

soup.find_all('span', attrs={'class':'datelk'})[0].get_text() # 년
soup.find_all('span', attrs={'class':'datelk'})[1].get_text() # 월

period = 1
month = 8
result_df = pd.DataFrame()

while period < 4:
    try:
        # 크롬드라이버 열기
        driver = wd.Chrome('C:\chromedriver') # 크롬드라이버 경로
        driver.maximize_window() # 크롬창 크기 최대

        # 드라이버가 해당 url 접속
        url = 'https://www.melon.com/chart/index.htm' # 멜론차트 페이지
        driver.get(url)
        time.sleep(2)

        # 차트파인더 클릭
        driver.find_element_by_xpath('//*[@id="gnb_menu"]/ul[1]/li[1]/div/div/button/span').click()
        time.sleep(2)

        # 월간차트 클릭
        driver.find_element_by_xpath('//*[@id="d_chart_search"]/div/h4[2]/a').click()
        time.sleep(2)

        driver.find_element_by_xpath('//*[@id="d_chart_search"]/div/div/div[1]/div[1]/ul/li[{}]/span/label'.format(period)).click()
        time.sleep(2)

        # 연도선택(규칙 찾기!)
        driver.find_element_by_xpath('//*[@id="d_chart_search"]/div/div/div[2]/div[1]/ul/li[2]/span/label').click()
        time.sleep(2)

        # 월선택 8월 클릭
        driver.find_element_by_xpath('//*[@id="d_chart_search"]/div/div/div[3]/div[1]/ul/li[{}]/span/label'.format(month)).click()
        time.sleep(2)

        # 장르선택 종합 클릭
        driver.find_element_by_xpath('//*[@id="d_chart_search"]/div/div/div[5]/div[1]/ul/li[1]/span/label').click()
        time.sleep(2)
        
        # 검색버튼 클릭
        driver.find_element_by_xpath('//*[@id="d_srch_form"]/div[2]/button/span/span').click()
        time.sleep(2)
        
        # html 정보 가져오기
        html = driver.page_source 
        soup = BeautifulSoup(html, 'lxml')
        
        # 노래 제목 가져오기
        song_list = [title.find('a').get_text() for title in soup.find_all('div', attrs={'class': 'ellipsis rank01'})]
        
        # 가수명 가져오기
        singer_list = [ singer.get_text() for singer in soup.find_all('span', attrs={'class':'checkEllipsis'}) ]
        
        # 순위 만들기
        rank_list = []
        for i in range(len(song)):
            rank_list.append(i+1)
        # 년
        year_list = list(repeat(soup.find_all('span', attrs={'class':'datelk'})[0].get_text(), len(song_list)))
        
        # 월 
        # month = list(repeat(soup.find_all('span', attrs={'class':'datelk'})[1].get_text(), len(song))) # 08로 표기되어 안깔끔
        month_list = list(repeat(month, len(song_list)))
        
        # 데이터프레임 생성
        df = pd.DataFrame({'연도':year_list,'월':month_list,'순위':rank_list,'곡명':song_list,'가수명':singer_list})
        result_df = pd.concat([result_df, df], ignore_index=True)
        period += 2
    
    except:
        print(period)
        break

result_df.to_csv('멜론차트크롤링.csv', encoding='ANSI')