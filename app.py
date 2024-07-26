import streamlit as st
import pandas as pd
import requests
import os

# API 키를 환경 변수에서 가져오거나 기본값을 설정
api_key = '150dae67776e945e520ac70e5ecaac21'

# 페이지 제목과 설명
st.title("Excel to Kakao Map")
st.markdown("## 엑셀 파일을 업로드하여 카카오 맵에 표시합니다.")
st.markdown("※ Excel 파일 A열은 주소지 명칭, B열은 주소")

# 엑셀 파일 업로드
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

# 엑셀 데이터 테이블 생성
if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # 데이터프레임 표시
    st.dataframe(df)

    # JSON 데이터로부터 위치 정보 추출
    positions = []
    geocoder_url = "https://dapi.kakao.com/v2/local/search/address.json?query={}"
    headers = {"Authorization": f"KakaoAK {api_key}"}

    # 주소를 위도 경도로 변환하여 positions 배열에 추가
    for index, row in df.iterrows():
        title = row[0]  # 엑셀의 첫 번째 열 데이터를 제목으로 사용
        address = row[1]  # 엑셀의 두 번째 열 데이터를 주소로 사용

        try:
            response = requests.get(geocoder_url.format(address), headers=headers)
            response.raise_for_status()  # 요청 실패 시 HTTPError 예외 발생
            result = response.json()
            if result['documents']:
                latitude = result['documents'][0]['y']
                longitude = result['documents'][0]['x']
                positions.append((title, address, latitude, longitude))
            else:
                st.error(f"Could not find coordinates for address: {address}")
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching coordinates for address: {address}. Error: {e}")

    # 위치 정보 표시
    if positions:
        st.map(pd.DataFrame(positions, columns=['title', 'address', 'lat', 'lon']))
    else:
        st.error("No valid positions to display on the map.")