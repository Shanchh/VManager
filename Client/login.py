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

lockfile = 'app.lock'

config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
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

    def login_VM(self):
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
            hwnd = get_active_window_hwnd()
            for index in self.VMword:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
                pyautogui.typewrite(index)
            
            pyautogui.press("enter")
            print(f"{get_time_now()}密碼輸入成功！")
        except Exception as e:
            print(f"{get_time_now()}自動輸入密碼失敗：{e}")

def startLogin():
    try:
        username = input(f"{get_time_now()}請輸入帳號：")
        password = input(f"{get_time_now()}請輸入密碼：")

        response = requests.post(f"{SERVER_URL}/login", json={"username": username, "password": password})
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success":
                client = Client(data['VMword'], VMRUN_PATH, VMX_PATH)
                client.login_VM()
                return
            else:
                print(f"{get_time_now()}密碼錯誤！")
        else:
            print(f"{get_time_now()}密碼錯誤！")

    except Exception as e:
        print(f"{get_time_now()}登入時發生錯誤, Error:{e}")
        return

def main():
    lock = FileLock(lockfile) # 檔案鎖
    try:
        lock.acquire(timeout=1)
    except Timeout:
        print("程序已在運行，禁止重複啟動。")
        time.sleep(3)
        return

    try:
        print_welcome()
        startLogin()
    finally:
        lock.release()

if __name__ == "__main__":
    main()