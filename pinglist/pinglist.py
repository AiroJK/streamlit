import time
from datetime import datetime
from ping3 import ping
import threading
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import Tk, Label, StringVar, Frame, Scale, HORIZONTAL, Button
import os
import subprocess

# 현재 스크립트의 디렉토리 경로
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 파일 경로
LOG_FILE_PATH = os.path.join(BASE_DIR, 'ping_results.txt')
PINGLIST_FILE_PATH = os.path.join(BASE_DIR, 'pinglist.txt')

# 초기 설정
PING_INTERVAL = 10
X_RANGE_HOURS = 1

# after 호출 취소 관리
AFTER_ID = None
THREAD_STOP_EVENT = threading.Event()

def process_line(line):
    """Process each line from the pinglist file and return a log entry."""
    site = line.strip().split()
    if len(site) < 2:
        return None
    
    ip, hostname = site[0], ' '.join(site[1:])
    result = ping(ip)
    status = f"Ping Check Fail" if result is None else f"Ping Check OK: [ Response Time {result:.2f} ]"
    return f"{datetime.now():%Y-%m-%d %H:%M:%S}\t{ip}\t{hostname}\t{status}\n"

def log_error(message):
    """Log errors to a file."""
    error_log_path = os.path.join(BASE_DIR, 'error_log.txt')
    with open(error_log_path, 'a') as error_log_file:
        error_log_file.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} - {message}\n")
        
def log_writer():
    """Continuously read pinglist file and write logs to the log file."""
    while not THREAD_STOP_EVENT.is_set():
        try:
            with open(PINGLIST_FILE_PATH, 'r') as f:
                lines = f.readlines()
            
            with open(LOG_FILE_PATH, 'a') as log_file:
                for line in lines:
                    if line.strip():
                        log_entry = process_line(line)
                        if log_entry:
                            log_file.write(log_entry)
        except Exception as e:
            log_error(f"Error writing log: {e}")
        time.sleep(PING_INTERVAL)

def read_pinglist_order():
    """Read the pinglist.txt file and return a list of hostnames in the order they appear."""
    try:
        with open(PINGLIST_FILE_PATH, 'r') as file:
            return [line.strip().split(maxsplit=1)[1] for line in file if line.strip()]
    except Exception as e:
        print(f"Error reading pinglist file: {e}")
        return []

def update_graph(frame):
    """Update the graph based on the latest log data."""
    try:
        df = pd.read_csv(LOG_FILE_PATH, sep='\t', header=None, names=['Timestamp', 'IP', 'Hostname', 'Status'])
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        df['Ping Check'] = df['Status'].apply(lambda x: 'Fail' if 'Fail' in x else 'OK')
        df['Response Time'] = df['Status'].str.extract(r'Response Time (\d+\.\d+)').astype(float)
        
        now = datetime.now()
        start_time = now - pd.DateOffset(hours=X_RANGE_HOURS)
        df = df[df['Timestamp'] >= start_time]

        min_y = df['Response Time'].dropna().min() if not df['Response Time'].dropna().empty else 0
        max_y = df['Response Time'].dropna().max() if not df['Response Time'].dropna().empty else 1

        ordered_hostnames = read_pinglist_order()
        unique_hostnames = df['Hostname'].unique()
        num_hostnames = len(unique_hostnames)

        fig.clf()
        axs = [fig.add_subplot(num_hostnames, 1, i + 1) for i in range(num_hostnames)]
        plt.subplots_adjust(left=0.1, right=0.75, hspace=0.5)

        for ax, hostname in zip(axs, ordered_hostnames):
            ax.clear()
            hostname_df = df[df['Hostname'] == hostname]
            
            df_ok = hostname_df[hostname_df['Ping Check'] == 'OK']
            df_fail = hostname_df[hostname_df['Ping Check'] == 'Fail']

            ax.plot(df_ok['Timestamp'], df_ok['Response Time'], marker='o', linestyle='-', color='b', label='Ping Check OK', markersize=3)
            ax.scatter(df_fail['Timestamp'], [0] * len(df_fail), color='r', marker='x', label='Ping Check Fail', s=100, zorder=5)
            
            ip_address = hostname_df['IP'].iloc[0] if not hostname_df.empty else 'Unknown IP'
            min_response_time = df_ok['Response Time'].min() if not df_ok.empty else None
            max_response_time = df_ok['Response Time'].max() if not df_ok.empty else None
            avg_response_time = df_ok['Response Time'].mean() if not df_ok.empty else None
            successful_pings = len(df_ok)
            total_pings = len(hostname_df)
            ping_success_rate = (successful_pings / total_pings) * 100 if total_pings > 0 else 0

            last_success_time = df_ok['Timestamp'].max() if not df_ok.empty else None
            last_fail_time = df_fail['Timestamp'].max() if not df_fail.empty else None
            current_state = 'OK' if last_success_time and (last_fail_time is None or last_success_time >= last_fail_time) else 'Fail'
            fail_time_delta = now - last_fail_time if current_state == 'Fail' and last_fail_time else None
            
            ax.set_title(f'Ping Check for {hostname} ({ip_address})')
            ax.set_xlabel('Timestamp')
            ax.set_ylabel('Response Time (ms)')
            ax.grid(True)
            ax.legend()
            ax.tick_params(axis='x', rotation=30)
            
            summary_text = (
                f'Current State: {current_state}\n'
                f'Last Success Date Time: {last_success_time.strftime("%Y-%m-%d %H:%M:%S") if last_success_time else "N/A"}\n'
                f'Ping Check Fail Time: {fail_time_delta if fail_time_delta else "N/A"}\n\n'
                f'Min Response Time: {min_response_time:.2f} ms\n'
                f'Max Response Time: {max_response_time:.2f} ms\n'
                f'Average Response Time: {avg_response_time:.2f} ms\n'
                f'Ping Success Rate: {ping_success_rate:.2f}% ({successful_pings:,}/{total_pings:,})'
            )
            
            if ax.texts:
                for text in ax.texts:
                    text.set_text(summary_text)
            else:
                ax.annotate(summary_text, xy=(1.05, 0.5), xycoords='axes fraction', fontsize=10, va='center', ha='left', bbox=dict(facecolor='white', alpha=0.8))
            
            ax.set_ylim(bottom=min_y, top=max_y)
            ax.set_xlim(start_time, now)
        
        last_update_var.set(f"Last Data Time: {df['Timestamp'].max() if not df.empty else 'No data'}")
        canvas.draw()
    except Exception as e:
        print(f"Error updating graph: {e}")

def update_interval(val):
    """Update the ping interval and refresh the plot."""
    global PING_INTERVAL
    PING_INTERVAL = int(val)
    print(f"Ping interval updated to: {PING_INTERVAL} seconds")
    refresh()

def update_x_range(val):
    """Update the x-axis range and refresh the graph."""
    global X_RANGE_HOURS
    X_RANGE_HOURS = int(val)
    print(f"X-axis range updated to: {X_RANGE_HOURS} hours")
    update_graph(None)

def open_file_with_notepad(file_path):
    """Open the specified file with Notepad (Windows)."""
    try:
        if os.name == 'nt':
            subprocess.run(['notepad.exe', file_path])
        else:
            print(f"Opening file in notepad is not supported for {os.name} OS.")
    except Exception as e:
        print(f"Error opening file: {e}")

def update_button_labels():
    """Update the labels of the file buttons."""
    try:
        if os.path.exists(PINGLIST_FILE_PATH):
            with open(PINGLIST_FILE_PATH, 'r') as file:
                line_count = len(file.readlines())
            pinglist_button.config(text=f"Open pinglist.txt ({line_count} lines)")
        else:
            pinglist_button.config(text="Open pinglist.txt (File not found)")
        
        if os.path.exists(LOG_FILE_PATH):
            file_size_kb = os.path.getsize(LOG_FILE_PATH) / 1024
            ping_result_button.config(text=f"Open ping_results.txt ({file_size_kb:,.2f} KB)")
        else:
            ping_result_button.config(text="Open ping_results.txt (File not found)")
    except Exception as e:
        print(f"Error updating button labels: {e}")

def refresh():
    """Refresh the graph periodically."""
    global AFTER_ID
    update_graph(None)
    AFTER_ID = root.after(PING_INTERVAL * 1000, refresh)

def on_closing():
    """Handle the window closing event."""
    global AFTER_ID
    global THREAD_STOP_EVENT
    if AFTER_ID is not None:
        root.after_cancel(AFTER_ID)
    THREAD_STOP_EVENT.set()
    root.quit()

def save_graph_image():
    """Save the current graph as an image file with a timestamp."""
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f'ping_graph_{now}.png'
    file_path = os.path.join(BASE_DIR, file_name)
    fig.savefig(file_path)
    print(f"Graph image saved to {file_path}")

# Tkinter 윈도우 생성
root = Tk()
root.title("Ping Check")

# 설정
fig = plt.figure(figsize=(15, 18))
canvas = FigureCanvasTkAgg(fig, master=root)

# 컨트롤 패널
control_frame = Frame(root)
control_frame.pack(side='top', fill='x', padx=10, pady=5)

# Ping 주기 설정
Label(control_frame, text="Ping Interval (seconds):").grid(row=0, column=0, padx=5, pady=2, sticky='w')
ping_var = StringVar(root, value='10')
ping_scale = Scale(control_frame, from_=1, to=60, orient=HORIZONTAL, variable=ping_var, command=update_interval)
ping_scale.grid(row=0, column=1, padx=5, pady=2)

# X축 범위 설정
Label(control_frame, text="X-axis Range (hours):").grid(row=1, column=0, padx=5, pady=2, sticky='w')
x_range_var = StringVar(root, value='1')
x_range_scale = Scale(control_frame, from_=1, to=24, orient=HORIZONTAL, variable=x_range_var, command=update_x_range)
x_range_scale.grid(row=1, column=1, padx=5, pady=2)

# 버튼들
pinglist_button = Button(control_frame, text="Open pinglist.txt", command=lambda: open_file_with_notepad(PINGLIST_FILE_PATH))
pinglist_button.grid(row=2, column=0, padx=5, pady=5, sticky='w')

ping_result_button = Button(control_frame, text="Open ping_results.txt", command=lambda: open_file_with_notepad(LOG_FILE_PATH))
ping_result_button.grid(row=2, column=1, padx=5, pady=5, sticky='w')

save_button = Button(control_frame, text="Save Graph Image", command=save_graph_image)
save_button.grid(row=2, column=2, padx=5, pady=5, sticky='w')

# Last update label
last_update_var = StringVar(root, value="Last Data Time: No data")
last_update_label = Label(control_frame, textvariable=last_update_var)
last_update_label.grid(row=3, column=0, columnspan=3, padx=5, pady=2, sticky='w')

# 그래프 캔버스 설정
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(fill='both', expand=True)

# Start log writer thread
log_thread = threading.Thread(target=log_writer, daemon=True)
log_thread.start()

# 그래프 업데이트 예약
refresh()

# 버튼 캡션 업데이트
update_button_labels()

# 이벤트 바인딩
root.protocol("WM_DELETE_WINDOW", on_closing)

# Tkinter 메인 루프 시작
root.mainloop()
