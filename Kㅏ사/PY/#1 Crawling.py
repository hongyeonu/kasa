from bs4 import BeautifulSoup
import re
import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
driver.implicitly_wait(2);

# 멜론 웹 페이지 접근

song_total = []

for month in range(1, 13):
    # 멜론 웹 페이지 접근
    driver.get('https://www.melon.com/chart/index.htm')
    driver.implicitly_wait(5)

    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="gnb_menu"]/ul[1]/li[1]/div/div/button/span')))

    driver.find_element(By.XPATH,'//*[@id="gnb_menu"]/ul[1]/li[1]/div/div/button').click()
    # driver.implicitly_wait(2);

    # 월간차트 클릭
    driver.find_element(By.XPATH,'//*[@id="d_chart_search"]/div/h4[2]/a').click()
    driver.implicitly_wait(2);

    # 연대선택 클릭
    driver.find_element(By.XPATH,'//*[@id="d_chart_search"]/div/div/div[1]/div[1]/ul/li[3]/span').click()
    driver.implicitly_wait(2);

    # 연도선택 클릭
    driver.find_element(By.XPATH,'//*[@id="d_chart_search"]/div/div/div[2]/div[1]/ul/li[2]/span').click()
    driver.implicitly_wait(2);

    # 월간선택 클릭
    driver.find_element(By.XPATH,f'//*[@id="d_chart_search"]/div/div/div[3]/div[1]/ul/li[{month}]/span').click()
    driver.implicitly_wait(2);

    # 국내종합 또는 종합 클릭
    #//*[@id="d_chart_search"]/div/div/div[5]/div[1]/ul/li[2]/span
    #//*[@id="d_chart_search"]/div/div/div[5]/div[1]/ul/li[3]/span/label

    # 초기 값 설정
    current_index = 1  # 시작할 인덱스
    max_index = 3  # 최대 시도할 인덱스

    while current_index <= max_index:
        try:
            # 시도할 XPath
            xpath = f'//*[@id="d_chart_search"]/div/div/div[5]/div[1]/ul/li[{current_index}]/span'
            
            # 해당 XPath의 엘리먼트를 찾음
            element = driver.find_element(By.XPATH, xpath)
            
            # label 태그의 텍스트를 확인
            label_text = element.find_element(By.TAG_NAME, 'label').text

            # label 태그에 글씨가 있으면 클릭
            if label_text:
                element.click()
                break
            else:
                print(f"XPath found, but label text is empty. Trying with index {current_index + 1}")
                current_index += 1
        except NoSuchElementException:
            # 해당 XPath를 찾을 수 없을 경우 다음 인덱스로 이동
            current_index += 1
            print(f"XPath not found. Trying with index {current_index}")
    # 이후의 코드 작성
    driver.implicitly_wait(2)

    # 검색 클릭
    driver.find_element(By.XPATH,'//*[@id="d_srch_form"]/div[2]/button').click()
    driver.implicitly_wait(2);


    # 모~든 가사들을 모으는 리스트
    all_titles = []
    all_artists = []
    all_genres = []
    all_likes = []
    all_lyrics = []


    #  가사정보 크롤링 함수
    def craw_lyrics():
        title = driver.find_elements(By.CLASS_NAME, 'song_name')
        artist = driver.find_elements(By.CLASS_NAME, 'artist_name')
        genre = driver.find_elements(By.CSS_SELECTOR, '#downloadfrm > div > div > div.entry > div.meta > dl > dd:nth-child(6)')
        like = driver.find_elements(By.CLASS_NAME, 'cnt')
        lyric = driver.find_elements(By.CLASS_NAME, 'lyric')
        driver.implicitly_wait(10)

        titles = []
        artists = []
        genres = []
        likes = []
        lyrics = []

        titles = title[0].text
        artists = artist[0].text
        genres = genre[0].text
        likes = like[0].text
        # lyrics = lyric[0].text

        all_titles.append(titles)
        all_artists.append(artists)
        all_genres.append(genres)
        all_likes.append(likes)

        if lyric:  # 가사가 존재하는 경우에만 추가
            lyrics = lyric[0].text
            all_lyrics.append(lyrics)
        else:
            all_lyrics.append('')  # 가사가 없으면 특정 메시지 추가
        

        # 공백 제거
        # lyrics = list(filter(None, lyrics))

        # 영어 제거
        # lyrics = list(filter(lambda i: i.upper() == i.lower(), lyrics))

        # for i in lyrics:
            #all_lyrics.append(i)
        print(titles, artists, lyrics)

    # data-song-no를 모으는 리스트
    song_num = []

    #lst50 = driver.find_elements(By.CLASS_NAME, 'btn_icon play')
    #lst100 = driver.find_elements(By.ID, 'lst100')
    #for i in lst50:
    #    song_num.append(i.get_attribute('data-song-no'))
    #for i in lst100:
    #    song_num.append(i.get_attribute('data-song-no'))
    numselect50 = '#lst50 > td:nth-child(4) > div > button.btn_icon.play'
    numselect100 = '#lst100 > td:nth-child(4) > div > button.btn_icon.play'

    num = driver.find_elements(By.CSS_SELECTOR, numselect50)
    for i in num:
        song_num.append(i.get_attribute('data-song-no'))
    num = driver.find_elements(By.CSS_SELECTOR, numselect100)
    for i in num:
        song_num.append(i.get_attribute('data-song-no'))

    print(len(song_num), song_num)
    song_total.append(len(song_num))

    # 상세 페이지 접근
    for i in range(len(song_num)):
        if song_num[i] is None:
            continue  # 다음 값으로 넘어가도록 처리
        driver.get('https://www.melon.com/song/detail.htm?songId={song_num}'.format(song_num=song_num[i]))
        craw_lyrics()

    fin_lyrics = []

    for i in range(len(all_lyrics)):
        fin_lyrics.append(all_lyrics[i].replace("\n", " "))

    rank = range(1,len(fin_lyrics)+1)

    df = pd.DataFrame({"rank": rank, "year": 2000, "month": f'{month}월', "title": all_titles, "artist": all_artists, "genre": all_genres, "like": all_likes, "lyric": fin_lyrics})
    df = df.set_index('rank')

    df.to_csv(f"2000_" + f"{month}.csv",  encoding='utf-8-sig')
