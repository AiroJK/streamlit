from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from urllib.request import urlretrieve
import os

# Headless 모드로 Chrome 브라우저 설정
chrome_options = Options()
chrome_options.add_argument('--headless')  # 브라우저를 표시하지 않음

# Selenium WebDriver로 브라우저 열기
driver = webdriver.Chrome(options=chrome_options)

# 이미지 저장 기준 폴더 생성
path_folder = 'my/img/'

if not os.path.isdir(path_folder):
    os.mkdir(path_folder)

# url 범위 설정
url_no = "0005339039"       # 시작url
url_no_end = "0005339040"   # 종료url
url_no_len = 10             # url_no 길이
category_no = "0000"        # 폴더 시작 no
category_len = 4            # 폴더no 길이

print("----- Start !!")

try:
    
    while int(url_no) <= int(url_no_end):
        # 웹 페이지 열기
        url = "https://n.news.naver.com/mnews/article/009/" + url_no
        driver.get(url)
        # driver.minimize_window()
        
        # 이미지 저장 하위 폴더 생성
        category_no = str(int(category_no) + 1).zfill(category_len)

        path_folder_temp = path_folder + category_no + "/"
        if not os.path.isdir(path_folder_temp):
            os.mkdir(path_folder_temp)

        # 모든 <img> 태그 찾기 (대기 시간 설정)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "img")))
        img_elements = driver.find_elements(By.CSS_SELECTOR, "img")

        # 각 이미지의 src 속성 출력
        i = 0
        for img in img_elements:
            src = img.get_attribute("src")
            class_name = img.get_attribute("class")
            if src and 'LAZY_LOADING' not in class_name:
                urlretrieve(src, path_folder_temp + f'{i:30}.jpg')        #link에서 이미지 다운로드, 파일명은 index와 확장자명으로
                i = i + 1

        print("----- In progress... " + url_no + " / " + category_no + " (Image Count : " + f'{i}' + ")")

        # 다음 url SET (url_no를 다음 숫자로 증가시키고 다시 10자리로 채움)
        url_no = str(int(url_no) + 1).zfill(url_no_len)

except WebDriverException as e:
    print(f"----- Failed to access URL: {url}")
    print(f"----- Error message: {str(e)}")

finally:
    # WebDriver 종료
    driver.quit()
    print("----- Complete !!  (Category Count : " + str(int(category_no)) + ")")
