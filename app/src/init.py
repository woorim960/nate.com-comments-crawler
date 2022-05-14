from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import time # 로딩 지연을 기다리기 위해 필요
import datetime # 엑셀 파일명 끝에 '날짜'를 추가하기 위해 필요 (엑셀 파일 이름의 중복을 피할 수 있음)

def get_chrome_driver():
  chrome_options = webdriver.ChromeOptions()
  driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
  return driver

def getUrls(inputs):
  SEARCHING_START_YEAR, SEARCHING_LAST_YEAR, SEARCHING_START_MONTH, SEARCHING_LAST_MONTH = inputs
  # 댓글 순으로 접속
  # 주간으로 바꾸기
  # 2020.01.1째 주 ~ 2022.04.4째 주 | 까지 검색
  url = "https://news.nate.com/rank/cmt?sc=&p=week&date="
  
  urls = []
  years = range(SEARCHING_START_YEAR, SEARCHING_LAST_YEAR + 1)
  monthes = range(SEARCHING_START_MONTH, SEARCHING_LAST_MONTH + 1)
  days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
  curr_year, curr_month, curr_day = map(int, datetime.datetime.now().strftime("%Y %m %d").split(" "))
  for year in years:
    day = 1
    for i, month in enumerate(list(monthes)):
      for day in range(1, days[i] + 1, 7):
        if year == curr_year and month >= curr_month and day > curr_day + 7:
          # 이번 주차 이후의 날짜는 검색하지 않게 해준다.
          return urls
        urls.append(url + f"{year}{(2 - len(str(month))) * '0' + str(month)}{(2 - len(str(day))) * '0' + str(day)}")
  return urls

def getCommentsAboutCorona(allComments, topic):
  # 댓글 중 '종교', '기독교', '예배', '신천지'가 포함된 댓글 반환
  result = []
  for comment in allComments:
    for keyword in ['종교', '기독교', '예배', '신천지']:
      if keyword in comment:
        cmt = comment.replace("\n", "").replace("\r", "")
        print(f"\n[댓글 수집]'{topic}' 관련 기사 중 '{keyword}' 관련 댓글을 수집합니다.\n{cmt}")
        result.append([keyword, cmt])
        break

  return result

def back(browser, year, month, day, rank):
  try:
    browser.back()
  except:
    print(f'\n{year}년 {month}월 {day}일 주차의 {rank}랭킹 게시판에서 뒤로가기를 실행하는 중 에러가 발생했습니다.\n에러가 무시되고 다음 주차를 탐색합니다.')
    time.sleep(5)
    browser.back()
    time.sleep(5)