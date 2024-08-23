import pandas as pd

def analyze_network_log(log_file='network_log.txt', threshold=100000):
    # 로그 파일을 읽어와 첫 줄을 헤더로 설정합니다
    df = pd.read_csv(log_file, delim_whitespace=True, header=0)
    
    # 데이터 프레임의 컬럼 이름과 데이터를 확인합니다
    print("Columns in the DataFrame:", df.columns)
    print(df.head())
    
    # 컬럼 이름을 명확하게 설정합니다
    df.columns = ['Time', 'Bytes_Sent', 'Sent_unit', 'Bytes_Received', 'Received_unit']
    
    # 불필요한 단위 문자열을 제거하고 숫자만 추출합니다
    df['Bytes_Sent'] = df['Bytes_Sent'].replace({'bytes/s': ''}, regex=True).str.replace(',', '').astype(int)
    df['Bytes_Received'] = df['Bytes_Received'].replace({'bytes/s': ''}, regex=True).str.replace(',', '').astype(int)
    
    # 데이터 확인
    print(df.head())
    
    # 평균 및 표준 편차 계산
    avg_sent = df['Bytes_Sent'].mean()
    std_sent = df['Bytes_Sent'].std()
    avg_received = df['Bytes_Received'].mean()
    std_received = df['Bytes_Received'].std()
    
    print(f"Average Bytes Sent: {avg_sent:,.0f}")
    print(f"Standard Deviation of Bytes Sent: {std_sent:,.0f}")
    print(f"Average Bytes Received: {avg_received:,.0f}")
    print(f"Standard Deviation of Bytes Received: {std_received:,.0f}")
    
    # 이상 징후 감지
    anomalies_sent = df[df['Bytes_Sent'] > (avg_sent + threshold)]
    anomalies_received = df[df['Bytes_Received'] > (avg_received + threshold)]
    
    if not anomalies_sent.empty:
        print("Anomalies detected in Bytes Sent:")
        print(anomalies_sent)
        
    if not anomalies_received.empty:
        print("Anomalies detected in Bytes Received:")
        print(anomalies_received)

if __name__ == "__main__":
    analyze_network_log()
