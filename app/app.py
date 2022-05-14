import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

import time # 로딩 지연을 기다리기 위해 필요
import pandas as pd # 액셀로 변환하기 위해 필요
import datetime # 엑셀 파일명 끝에 '날짜'를 추가하기 위해 필요 (엑셀 파일 이름의 중복을 피할 수 있음)

SEARCHING_START_YEAR = int(input("탐색의 시작 연도를 입력해주세요(ex: 2020) > "))
SEARCHING_LAST_YEAR = int(input("탐색의 마지막 연도를 입력해주세요(ex: 2021) > "))
SEARCHING_START_MONTH = int(input("탐색의 시작 월을 입력해주세요(ex: 1) > "))
SEARCHING_LAST_MONTH = int(input("탐색의 마지막 월을 입력해주세요(ex: 12) > "))
COMMENT_SERACHING_START_PAGE = int(input("각 게시판의 댓글을 몇번 Page부터 검색하시겠습니까? (ex: 1) > "))
COMMENT_SERACHING_LAST_PAGE = int(input("각 게시판의 댓글을 몇번 Page까지 검색하시겠습니까? (ex: 10) > "))
SEARCHING_START_RANK = 1 # 랭크 1위부터 검색
SEARCHING_LAST_RANK = 30 # 30위 까지가 최대임

def get_chrome_driver():
  chrome_options = webdriver.ChromeOptions()
  driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
  return driver

def getUrls():
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

def back(year, month, day, rank):
  try:
    browser.back()
  except:
    print(f'\n{year}년 {month}월 {day}일 주차의 {rank}랭킹 게시판에서 뒤로가기를 실행하는 중 에러가 발생했습니다.\n에러가 무시되고 다음 주차를 탐색합니다.')
    time.sleep(5)
    browser.back()
    time.sleep(5)

# 크롬 브라우저를 실행할 도구 가져오기
browser = get_chrome_driver()
wait  = WebDriverWait(browser, 10) # 로딩 안됐을 때 10초까지 기다리게 해주는 도구 가져오기
print()

# 데이터 수집 시작
urls = getUrls()
# urls = ["https://news.nate.com/rank/cmt?sc=&p=week&date=20220401"]
comments = []
for url in urls:
  date = url.split("=")[-1]
  year = date[:4]
  month = date[4:6]
  day = date[6:]
  print(f"\n*************************  {year}년 {month}월 {day}일 주차의 기사를 탐색합니다  *************************")
  browser.get(url)
  for i in range(SEARCHING_START_RANK, SEARCHING_LAST_RANK + 1):
    try:
      if i <= 5:
        # rank{1} 이상 {5} 이하는 형제 노드 중 'mlt01' 클래스 태그의 자식 중 'tit' 클래스 태그의 text가 기사 제목임
        title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f'.rank{i} + .mlt01 .tit')))
      else:
        # rank{6} 이상은  형제 노드 중 'a' 태그의 text가 기사 제목임.
        title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f'.rank{i} + a')))
    except:
      print(f"\nError: {year}.{month}.{day} 주차에는 {i}번 째 랭킹의 게시글이 존재하지 않습니다.\n에러가 무시되고 다음 주차를 탐색합니다.")
      # 브라우저 뒤로가기
      back(year, month, day, i)
      break

    # '코로나' 혹은 '오미크론' 이 포함된 기사 추출
    searching_keywords = ['코로나', '오미크론']
    news_title = title.text
    for keyword in searching_keywords:
        if keyword in news_title:
            # keyword가 포함된 뉴스를 클릭하여 이동
            print(f"\n[기사 클릭]'{keyword}' 관련 뉴스 기사({year}.{month}.{day}주차 / {i}랭킹)를 클릭합니다.\n{news_title}")
            try:
              title.click()
              wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f'#articleView')))
              artc_sq = browser.current_url.split("?")[0].split("/")[-1]
            except:
              print("\nError: '코로나' 관 련 기사 제목 클릭 중 에러가 발생했습니다.\n에러가 무시되고 다음 게시글을 탐색합니다.")
              # 브라우저 뒤로가기
              back(year, month, day, i)
              break

            commentsInSamePost = []
            for commentPage in range(COMMENT_SERACHING_START_PAGE, COMMENT_SERACHING_LAST_PAGE + 1):
              try:
                requestUrl = f"https://comm.news.nate.com/Comment/ArticleComment/List?artc_sq={artc_sq}&order=&cmtr_fl=0&prebest=0&clean_idx=&user_nm=&fold=&mid=n1006&domain=&argList=0&best=1&return_sq=&connectAuth=N&page={commentPage}#comment"
                print(f"\n{commentPage} 페이지의 댓글을 탐색합니다.")
              except:
                print("\nError: 댓글 자료 요청 중 에러가 발생했습니다.\n에러가 무시되고 다음 게시글을 탐색합니다.")
                break
              html = requests.get(requestUrl).content
              soup = BeautifulSoup(html, 'html.parser')
              allComments = list(map(lambda x: x.text.replace("\t", ""), soup.select(".usertxt")))
              
              if len(allComments) <= 0: 
                # 더이상 댓글이 없으면 탐색 종료
                break

              # 댓글 중 '종교', '기독교', '예배', '신천지'가 포함된 댓글 수집
              foundComments = getCommentsAboutCorona(allComments, keyword)
              # if commentPage >= 3 and len(commentsInSamePost) <= 0: 
              #   # 3페이지까지 탐색했는데 '기독교' 관련 댓글이 없으면, 이후로도 없을 것으로 판단하여 다음 게시글을 탐색하도록 합니다.
              #   break
              for foundComment in foundComments:
                commentsInSamePost.append([year, month, day, keyword, news_title, *foundComment, url])
            
            comments += commentsInSamePost
            # 브라우저 뒤로가기
            back(year, month, day, i)
            break
        
    print(".", end="")

browser.quit()

df = pd.DataFrame(comments, columns=['년도', '월', '일(의 주차)', '기사 키워드', '기사 제목', '댓글 키워드', '댓글', 'URL']) # index=['댓글'], 
print(df)

# 엑셀 파일 저장
df.to_excel(f'./excel-files/covid_{datetime.datetime.now().strftime("%Y%m%d_%I%m%S")}.xlsx', sheet_name='new_name')