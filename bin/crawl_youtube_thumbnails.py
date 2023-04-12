from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from PyQt5.QtWidgets import *
from bs4 import BeautifulSoup
import time
import urllib
import random
import re
import pandas as pd
import os
class YCrawler():
    def __init__(self, parent):
        self.parent = parent
        self.driver = None
        self.img_search_page = None
        self.valid_num = None
        self.title = None
        self.img_url = None
        self.link = None
        self.view_count = None
        self.posted_date = None
        self.source = None
        self.relevant_keywords = None
        self.data = []
        self.data_frame = []
        self.count = 1
    
    def start_crawling(self):
        print('=========================================================================================================')
        print('=========================================================================================================')
        print("지금부터 요청하신 크롤링 작업을 시작합니다. 조금만 기다려 주세요")
    
    # 초기 드라이버 세팅하기
    def set_init_driver(self, chrome_options):
        chrome_options.add_argument('headless')
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
        time.sleep(1)
    # 유투브 이미지 사이트 로딩하기
    def load_searching_page(self, search_key):
        for i in search_key.split():
                if ':' in i:
                    search_key = '+'.join(e for e in search_key.split()[1:])
        search_key = '+'.join(e for e in search_key.split())
        self.img_search_page = f'https://www.youtube.com/results?search_query={search_key}'
        self.driver.get(url=self.img_search_page)
        self.driver.implicitly_wait(time_to_wait=10)
    # 찾는 개수중에서 숫자만 parsing해오기
    def validate_num_images(self, num):
        for i in num.split():
            if ':' in i:
                self.valid_num = re.findall(r'\d+', num[1:])[0]
        self.valid_num =  re.findall(r'\d+', num)[0]
    # 랜덤한 시간만큼 시간을 멈추게 하기
    def set_random_time_out(self):
        return time.sleep(random.uniform(0.3, 0.7))
    # 10번 정도 스크롤을 내리기
    def scroll_down_x_times(self, scroll_times):
        bodyElement = self.driver.find_element(By.TAG_NAME, 'body')
        for i in scroll_times.split():
            if ':' in i:
                total_scroll_times = int(re.findall(r'\d+', scroll_times[1:])[0])//10
            else:
                total_scroll_times = int(re.findall(r'\d+', scroll_times)[0])//10
        for i in range(total_scroll_times):
            bodyElement.send_keys(Keys.END)
            time.sleep(0.5)
        time.sleep(2.5)
            # self.driver.implicitly_wait(1)
    # 검색 된 사진 한장 한장 클릭하면서 HD 이미지 다운로드 하기
    def get_all_relevent_contents(self):
        # 썸네일 카드 추출
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        # 검색 결과 영상 리스트 추출
        # thumbnails = soup.find_all("div", {"class": "text-wrapper style-scope ytd-video-renderer"})
        thumbnails = soup.find_all("div", {"id": "dismissible"})
        print("현재 썸네일의 길이는 ", len(thumbnails))
        # 각 영상 정보 크롤링
        for thumbnail in thumbnails:
            #썸네일 제목 추출
            try:
                self.title = thumbnail.find('a', {'id': "video-title"}).text.replace('\n', '')
            except:
                self.title = 'N/A'
            # 썸네일 이미지 url 추출
            try:
                # #thumbnail > yt-image > img
                self.img_url = thumbnail.find("img")['src']
            except:
                self.img_url = 'N/A'
            # 썸네일 비디오 링크 추출
            try:
                self.link = "https://www.youtube.com" + thumbnail.find('a', {'class': "yt-simple-endpoint style-scope ytd-video-renderer"}).get('href')
            except:
                self.link = 'N/A'
            # 영상 조회수 추출
            try:
                self.view_count = thumbnail.find("div", {"id": "metadata-line"}).text.split('\n')[3]
            except:
                self.view_count = 'N/A'
            # 영상 업로드 시점 추출
            try:
                self.posted_date = thumbnail.find("div", {"id": "metadata-line"}).text.split('\n')[4]
            except:
                self.posted_date = 'N/A'
            # 썸네일 출처 추출
            try:
                self.source = thumbnail.find("div", {"id": "text-container"}).text.replace('\n', '')
            except:
                self.source = 'N/A'
            # 해시태그 키워드 추출
            try:
                self.relevant_keywords = thumbnail.find("div", {"class": "metadata-snippet-container style-scope ytd-video-renderer style-scope ytd-video-renderer"}).text.split()
            except:
                self.relevant_keywords = 'N/A'
            # 각 정보 출력
            print(self.count)
            print(f'self.title: {self.title}')
            print(f'self.img_url: {self.img_url}')
            print(f'self.link', {self.link})
            print(f'view count: {self.view_count}')
            print(f'posted date: {self.posted_date}')
            print(f'self.source: {self.source}')
            print(f'relevant keywords: {self.relevant_keywords}')
            print('\n')
            
            if self.title != 'N/A' and self.img_url != 'N/A':
                self.count += 1
                self.data.append([self.title, self.img_url, self.link, self.view_count, self.posted_date, self.source, self.relevant_keywords])
    def write_data_to_the_csv_file(self):
        self.data_frame = pd.DataFrame(self.data, columns=['title', 'img url', 'link', 'view count', 'posted date', 'source', 'relevant keywords'])
        self.data_frame.index = range(1, len(self.data_frame) + 1)
        self.data_frame.to_csv(os.path.normpath(os.path.join(self.parent.save_file_line_edit.text(), 'youtube_thumbnails.csv')), encoding='utf-8-sig', index=True)
    
    def end_crawling(self):
        print('=========================================================================================================')
        print('=========================================================================================================')
        print("모든 크롤링이 정상적으로 종료되었습니다. 저장된 디렉토리에 가서 `youtube_thumbnails.csv` 파일을 한번 열어보세요!")

    def run(self):
        self.start_crawling()
        self.set_init_driver(webdriver.ChromeOptions())
        self.load_searching_page(self.parent.search_line_edit.text())
        self.scroll_down_x_times(self.parent.max_num_line_edit.text())
        self.get_all_relevent_contents()
        self.write_data_to_the_csv_file()
        self.parent.time_worker.working = False
        self.end_crawling()