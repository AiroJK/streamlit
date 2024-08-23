import os
import sys

def get_data_file_path(file_name):
    """ 실행 파일의 디렉토리 또는 현재 작업 디렉토리에서 파일 경로를 반환합니다. """
    if getattr(sys, 'frozen', False):
        # PyInstaller로 패키징된 경우
        base_path = os.path.dirname(sys.executable)
    else:
        # 개발 환경에서 실행 중
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, file_name)

LOG_FILE_PATH = get_data_file_path('ping_results.txt')
PINGLIST_FILE_PATH = get_data_file_path('pinglist.txt')

print(f"LOG_FILE_PATH: {LOG_FILE_PATH}")
print(f"PINGLIST_FILE_PATH: {PINGLIST_FILE_PATH}")

# 파일 존재 여부 확인
print(f"LOG_FILE exists: {os.path.exists(LOG_FILE_PATH)}")
print(f"PINGLIST_FILE exists: {os.path.exists(PINGLIST_FILE_PATH)}")