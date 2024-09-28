import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import math###역대급으로 가장 잘된 파이썬 코드 카카오맵 크롤링 9월 28일 오후 4시 기준
# Chrome 드라이버 경로 설정
driver_path = "./chromedriver.exe"
service = Service(driver_path)
driver = webdriver.Chrome(service=service)

# 카카오맵 URL
source_url = "https://map.kakao.com/"
driver.get(source_url)

# 검색창 찾기 및 검색
search = driver.find_element(By.XPATH, '//*[@id="search.keyword.query"]')
search.send_keys("쎈느")
search.send_keys(Keys.ENTER)
time.sleep(5)  # 페이지 로딩 대기 시간 증가

# 리뷰 페이지 URL 가져오기
html = driver.page_source
soup = BeautifulSoup(html, "html.parser")
moreviews = soup.select("a.moreview")  # 더보기 버튼 선택자 변경

if moreviews:
    ramen_url = moreviews[0].get("href")
    print("리뷰 페이지 URL:", ramen_url)
else:
    print("리뷰 페이지 URL을 찾을 수 없습니다.")
    driver.quit()
    exit()

columns=['score','review']
df=pd.DataFrame(columns=columns)
stars=[]#별점
reviews=[]
driver=webdriver.Chrome(service=service)
driver.get(ramen_url)

last_height=driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Corrected line
    time.sleep(2)
    # 스크롤 내려서 높이를 다시 가져옴
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height
    tmp = driver.page_source
    tmp2 = BeautifulSoup(tmp, 'html.parser')
    total_reviews = int(tmp2.select('#mArticle > div.cont_evaluation > strong.total_evaluation > span.color_b')[0].get_text())
    print("총 후기수:",total_reviews)
    pages = math.ceil(total_reviews / 5)
    print("페이지 개수:",pages)
    time.sleep(5)
    break
    
# 페이지 개수 만큼 '후기 더보기' 버튼 클릭
for i in range(pages):
    try:
        more_button = driver.find_element(By.CSS_SELECTOR, '#mArticle > div.cont_evaluation > div.evaluation_review > a')
        more_button.click()
        print(f'{i+1}번째 후기 더보기 버튼 클릭')
        time.sleep(2)  # 페이지 로딩 대기 시간
    except:
        print("후기 더보기 버튼이 더 이상 존재하지 않습니다.")
        break

html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
review_blocks = soup.select('#mArticle > div.cont_evaluation > div.evaluation_review > ul > li')

# 각 리뷰 블록을 순회하며 별점과 리뷰를 추출
for block in review_blocks:
    # 별점 추출
    star_tag = block.select_one('span.ico_star.inner_star')  # 올바른 선택자로 변경
    
    # star_tag가 존재하는지 확인
    if star_tag and 'style' in star_tag.attrs:
        style_width = star_tag['style']  # style 속성에서 별점 정보 추출
        width = int(style_width.split(":")[1].strip().strip(';').replace('%', ''))
        rating = width / 20  # 별점 계산
        stars.append(rating)
    else:
        print("별점 정보를 찾을 수 없습니다.")
    # 리뷰 텍스트 추출
    review_tag = block.select_one('p.txt_comment > span')
    if review_tag:
        review_text = review_tag.get_text(strip=True)
    else:
        review_text = ''  # 리뷰가 없을 경우 빈 문자열
    # 결과 출력
    reviews.append(review_text)
    print(f'별점: {rating}, 리뷰: "{review_text}"')
    
print(len(stars))#188확인됨
print(len(reviews))#188확인됨
driver.close()
# DataFrame 생성 및 CSV로 저장
df = pd.DataFrame({'rating': stars, 'review': reviews})
df.to_csv('쎈느.csv', encoding='utf-8-sig', index=False)