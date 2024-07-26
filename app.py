import streamlit as st
import pandas as pd
import os
import json

# API 키를 환경 변수에서 가져오거나 기본값을 설정
api_key = os.environ.get('API_KEY') or '150dae67776e945e520ac70e5ecaac21'

# 페이지 제목과 설명
st.title("Excel to Kakao Map")
st.markdown("## 엑셀 파일을 업로드하여 카카오 맵에 표시합니다.")
st.markdown("※ Excel 파일 A열은 주소지 명칭, B열은 주소")

# API 키 표시
st.markdown(f"**API Key**: {api_key}")

# 엑셀 파일 업로드
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

# 맵을 표시할 div 생성
map_div = st.empty()

# 엑셀 데이터 테이블 생성
if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # 데이터프레임 표시
    st.dataframe(df)

    # JSON 데이터로부터 위치 정보 추출
    positions = []
    geocoder_url = f"https://dapi.kakao.com/v2/local/search/address.json?query={{}}&key={api_key}"
    headers = {"Authorization": f"KakaoAK {api_key}"}

    # 주소를 위도 경도로 변환하여 positions 배열에 추가
    for index, row in df.iterrows():
        title = row[0]  # 엑셀의 첫 번째 열 데이터를 제목으로 사용
        address = row[1]  # 엑셀의 두 번째 열 데이터를 주소로 사용
        response = requests.get(geocoder_url.format(address), headers=headers)
        if response.status_code == 200:
            result = response.json()
            if result['documents']:
                latitude = float(result['documents'][0]['y'])
                longitude = float(result['documents'][0]['x'])
                positions.append({"title": title, "latlng": {"lat": latitude, "lng": longitude}})
            else:
                st.error(f"위도와 경도를 찾을 수 없습니다: {address}")
        else:
            st.error(f"주소 변환 중 오류가 발생했습니다: {address}")

    # 카카오 맵 생성
    if positions:
        map_options = {
            "center": {"lat": positions[0]["latlng"]["lat"], "lng": positions[0]["latlng"]["lng"]},
            "level": 7
        }
        markers = [{"title": p["title"], "latlng": p["latlng"]} for p in positions]

        # 맵과 마커를 포함한 HTML 코드 생성
        map_html = f"""
        <div id="map" style="width:100%;height:600px;"></div>
        <script type="text/javascript" src="//dapi.kakao.com/v2/maps/sdk.js?appkey={api_key}&libraries=services"></script>
        <script>
            var mapContainer = document.getElementById('map');
            var mapOption = {{
                center: new kakao.maps.LatLng({map_options['center']['lat']}, {map_options['center']['lng']}),
                level: {map_options['level']}
            }};
            var map = new kakao.maps.Map(mapContainer, mapOption);

            var markers = {json.dumps(markers)};
            markers.forEach(function(marker) {{
                var markerPosition  = new kakao.maps.LatLng(marker.latlng.lat, marker.latlng.lng);
                var marker = new kakao.maps.Marker({{
                    position: markerPosition,
                    title: marker.title
                }});
                marker.setMap(map);
                var infowindow = new kakao.maps.InfoWindow({{
                    content: '<div style="padding:5px;">' + marker.title + '</div>'
                }});
                kakao.maps.event.addListener(marker, 'mouseover', function() {{
                    infowindow.open(map, marker);
                }});
                kakao.maps.event.addListener(marker, 'mouseout', function() {{
                    infowindow.close();
                }});
            }});
        </script>
        """
        map_div.markdown(map_html, unsafe_allow_html=True)
    else:
        st.error("유효한 주소를 포함한 데이터가 없습니다.")
