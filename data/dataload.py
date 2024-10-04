import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import math

#Chrome 드라이버 경로 설정
driver_path = "./chromedriver.exe"
service = Service(driver_path)
driver = webdriver.Chrome(service=service)

restaurant_df = pd.read_csv("restaurant.csv")  # CSV 파일 이름을 수정하세요

for index, row in restaurant_df.iterrows():
    # if index<3:#필요에 따라 restaurant.csv파일에서 원하는 식당들만 인덱스 슬라이싱해서 가져올 수도 있어서 해봤음
    #     continue
    name = row['name']
    url = row['urls']
    print(f"{name}의 후기를 크롤링합니다.")

    driver.get(url)
    time.sleep(5)  #페이지 로딩 대기
    #페이지 스크롤
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    #스크롤이 완료된 후 HTML 가져오기
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    #총 후기 수 가져오기
    total_reviews = int(soup.select('#mArticle > div.cont_evaluation > strong.total_evaluation > span.color_b')[0].get_text())
    print("총 후기수:", total_reviews)
    pages = math.ceil(total_reviews / 5)  # 1페이지에 5개 리뷰
    print("페이지 개수:", pages)
    stars=[]#ratings
    reviews=[]#review texts

    #페이지 개수만큼 모든 '후기더보기'버튼 클릭해서 데이터 전부 가져오기
    for i in range(pages):
        try:
            more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '#mArticle > div.cont_evaluation > div.evaluation_review > a'))
            )
            ActionChains(driver).move_to_element(more_button).click().perform()
            print(f'{i + 1}번째 후기 더보기 버튼 클릭')
            time.sleep(2)  # 페이지 로딩 대기 시간
        except Exception as e:
            print(f"후기 더보기 버튼 클릭 중 오류 발생: {e}")
            print("후기 더보기 버튼이 더 이상 존재하지 않습니다.")
            break

    #모든 리뷰 블록 선택
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    review_blocks = soup.select('#mArticle > div.cont_evaluation > div.evaluation_review > ul > li')

    #각 리뷰 블록을 순회하며 별점과 리뷰를 추출
    for block in review_blocks:
        #별점 추출
        star_tag = block.select_one('span.ico_star.inner_star')  # 올바른 선택자로 변경
        #별점이 존재하는지 확인
        if star_tag and 'style' in star_tag.attrs:
            style_width = star_tag['style']  # style 속성에서 별점 정보 추출
            width = int(style_width.split(":")[1].strip().strip(';').replace('%', ''))
            rating = width / 20  # 별점 계산
            stars.append(rating)
        else:
            print("별점 정보를 찾을 수 없습니다.")
            stars.append(None)  # 별점 정보가 없으면 None 추가
        #리뷰 텍스트 추출
        review_tag = block.select_one('p.txt_comment > span')
        if review_tag:
            review_text = review_tag.get_text(strip=True)
        else:
            review_text = ''  # 리뷰가 없을 경우 빈 문자열
        
        #결과 저장
        reviews.append(review_text)
        print(f'별점: {rating}, 리뷰: "{review_text}"')

    # 리뷰 수 확인
    # print(len(stars))  
    # print(len(reviews)) 
    #DataFrame 생성 및 CSV 파일 저장
    df = pd.DataFrame({'rating': stars[:total_reviews], 'review': reviews[:total_reviews]})
    csv_filename = f'data/{name}.csv'  
    df.to_csv(csv_filename, encoding='utf-8-sig', index=False)
    print(f"{csv_filename} 파일로 저장되었습니다.")
driver.quit()
