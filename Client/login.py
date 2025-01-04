import win32con
import win32gui
import requests
import subprocess
import pyautogui
import time
import configparser
import os
from datetime import datetime
from filelock import FileLock, Timeout
import getpass
import sys
from collections import Counter

FIREBASE_API_KEY = "AIzaSyABKsYLS-KImX4S1TvM_vYoyAIFyrENnr4"

lockfile = 'app.lock'

def get_executable_dir():
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

config_path = os.path.join(get_executable_dir(), 'config.ini')
config = configparser.ConfigParser()
config.read(config_path, encoding='utf-8')

USER_NAME = config['setting']['user_name']
VMRUN_PATH = config['setting']['vmrun_path'].replace('\\', '\\\\')
VMX_PATH = config['setting']['vmx_path'].replace('\\', '\\\\')
START_DELAY = int(config['setting']['start_delay'])
SERVER_URL = config['setting']['server_ip']

def get_time_now():
    return f"[{datetime.now().strftime('%H:%M:%S')}] "

def get_active_window_hwnd():
    hwnd = win32gui.GetForegroundWindow()
    return hwnd

def print_welcome():
    print("┍" + "━" * 26 + "┑")
    print("│" + " " * 5 + "VManager登入系統"+ " " * 5 + "│")
    print("┕" + "━" * 26 + "┙")

class Client:
    def __init__(self, VMword, vmrun_path, vmx_path):
        self.VMword = VMword
        self.vmrun_path = vmrun_path
        self.vmx_path = vmx_path

    def login_VM(self, hwnd):
        counter = Counter(hwnd)
        most_common = counter.most_common(1)
        value, count = most_common[0]

        self.hwnd = int(value)

        self.start_vm()
        self.auto_login_with_pyautogui()

    def start_vm(self):
        """異步啟動虛擬機"""
        try:
            print(f"{get_time_now()}正在啟動虛擬機...")
            subprocess.Popen([self.vmrun_path, "start", self.vmx_path])
            print(f"{get_time_now()}已發送虛擬機啟動請求！")
        except Exception as e:
            print(f"{get_time_now()}虛擬機啟動失敗：{e}")

    def auto_login_with_pyautogui(self):
        """使用 pyautogui 自動輸入密碼"""
        try:
            print(f"{get_time_now()}等待虛擬機登入介面加載...請不要做任何動作!!!")
            time.sleep(START_DELAY)

            print("自動輸入密碼中...")
            # pyautogui.hotkey('shift')

            for index in self.VMword:
                focus_window(self.hwnd)
                pyautogui.typewrite(index)
            
            pyautogui.press("enter")
            print(f"{get_time_now()}密碼輸入成功！")
        except Exception as e:
            print(f"{get_time_now()}自動輸入密碼失敗，請重新執行程式")

def focus_window(hwnd):
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.SetForegroundWindow(hwnd)

def startLogin(start_hwnd):
    try:
        while True:
            hwnd = []
            hwnd.append(start_hwnd)
            email = input(f"{get_time_now()}請輸入信箱：")
            hwnd.append(get_active_window_hwnd())
            password = getpass.getpass(f"{get_time_now()}請輸入密碼：")
            hwnd.append(get_active_window_hwnd())

            print(f"{get_time_now()}登入中請稍後....")

            firebase_login_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
            payload = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }

            response = requests.post(firebase_login_url, json=payload)

            if response.status_code == 200:
                data = response.json()
                id_token = data["idToken"]
                if postLogin(email, id_token, hwnd):
                    print(f"{get_time_now()}程式即將結束。")
                    sys.exit(0)
            else:
                error_info = response.json().get("error", {}).get("message", "Unknown error")
                print(f"{get_time_now()}登入失敗！原因：{error_info}\n━")

    except Exception as e:
        print(f"{get_time_now()}登入時發生錯誤, Error:{e}")
        return

def postLogin(email, id_token, hwnd, max_retries=10):
    retry_count = 0
    while retry_count < max_retries:
        response = requests.post(f"{SERVER_URL}/login", json={"username": USER_NAME, "email": email, "password": id_token})
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                client = Client(data['VMword'], VMRUN_PATH, VMX_PATH)
                client.login_VM(hwnd)
                return True
            else:
                print(f"{get_time_now()}密碼錯誤！\n━")
                return False
        else:
            try:
                error_detail = response.json().get("detail", "Unknown error")
                print(f"{get_time_now()}登入失敗！原因：{error_detail}\n━")
                return False
            except ValueError:
                pass
        retry_count += 1
        time.sleep(2)

    print(f"{get_time_now()}登入重試次數已達上限 ({max_retries})\n━")
    return False

def main(start_hwnd):
    lock = FileLock(lockfile) # 檔案鎖
    try:
        lock.acquire(timeout=1)
    except Timeout:
        print("程序已在運行，禁止重複啟動。")
        time.sleep(3)
        return

    try:
        print_welcome()
        startLogin(start_hwnd)
    finally:
        lock.release()

if __name__ == "__main__":
    start_hwnd = get_active_window_hwnd()
    main(start_hwnd)