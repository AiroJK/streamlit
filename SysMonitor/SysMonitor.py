import psutil
import time
import os
from datetime import datetime

def get_system_stats():
    """현재 시스템의 CPU, 메모리, 디스크 I/O 통계 가져오기"""
    net_io = psutil.net_io_counters()
    cpu_usage = psutil.cpu_percent(interval=None)  # 인터벌을 None으로 설정하여 즉시 측정
    memory_info = psutil.virtual_memory()
    disk_io = psutil.disk_io_counters()
    
    return {
        'net_io': net_io,
        'cpu_usage': cpu_usage,
        'memory_used': memory_info.used,
        'memory_total': memory_info.total,
        'disk_read': disk_io.read_bytes,
        'disk_write': disk_io.write_bytes
    }

def get_log_filename(base_name='system_log', max_size_mb=10):
    """파일 롤링을 위한 로그 파일 이름 생성"""
    log_file = f"{base_name}.txt"
    if os.path.exists(log_file):
        if os.path.getsize(log_file) > max_size_mb * 1024 * 1024:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_file = f"{base_name}_{timestamp}.txt"
    return log_file

def monitor_system(interval=1, max_file_size_mb=10, log_base='system_log'):
    """시스템 통계를 모니터링하고 로그 파일에 저장"""
    log_file = get_log_filename(log_base, max_file_size_mb)
    
    # 로그 파일이 존재하지 않는 경우 헤더를 작성합니다.
    file_exists = os.path.isfile(log_file)
    if not file_exists:
        with open(log_file, 'w') as f:
            f.write(f"{'Time':<10} {'CPU Usage (%)':<15} {'Memory Used (MB)':<20} {'Memory Total (MB)':<20} {'Disk Read (MB)':<20} {'Disk Write (MB)':<20} {'Bytes Sent (B/s)':<20} {'Bytes Received (B/s)':<20}\n")
    
    prev_net_io = get_system_stats()['net_io']
    prev_sent = prev_net_io.bytes_sent
    prev_recv = prev_net_io.bytes_recv
    prev_disk_io = get_system_stats()['disk_read']
    
    while True:
        start_time = time.time()
        stats = get_system_stats()
        net_io = stats['net_io']
        sent = net_io.bytes_sent
        recv = net_io.bytes_recv
        
        sent_rate = (sent - prev_sent) / interval
        recv_rate = (recv - prev_recv) / interval
        
        disk_read = stats['disk_read']
        disk_read_rate = (disk_read - prev_disk_io) / interval
        
        prev_sent = sent
        prev_recv = recv
        prev_disk_io = disk_read

        log_entry = (
            f"{time.strftime('%H:%M:%S'):<10} "
            f"{stats['cpu_usage']:>15} "
            f"{stats['memory_used'] / (1024 * 1024):>20,.0f} "
            f"{stats['memory_total'] / (1024 * 1024):>20,.0f} "
            f"{disk_read_rate / (1024 * 1024):>20,.0f} "
            f"{stats['disk_write'] / (1024 * 1024):>20,.0f} "
            f"{sent_rate:>20,.0f} "
            f"{recv_rate:>20,.0f}\n"
        )
        
        # 파일에 로그를 추가합니다.
        with open(log_file, 'a') as f:
            f.write(log_entry)
        
        print(log_entry, end='')
        
        # 정확한 간격을 유지하기 위해 시간 차이를 계산하여 조정합니다.
        elapsed_time = time.time() - start_time
        time.sleep(max(0, interval - elapsed_time))
        
        # 파일 크기를 체크하고 필요시 파일 롤링
        if os.path.getsize(log_file) > max_file_size_mb * 1024 * 1024:
            log_file = get_log_filename(log_base, max_file_size_mb)

if __name__ == "__main__":
    monitor_system()
