import asyncio
import websockets
import requests
import subprocess
import pyautogui
import time
import win32gui
import win32con
from datetime import datetime
import atexit
import subprocess
import sys
import ctypes
import configparser
from filelock import FileLock, Timeout

import manage

lockfile = 'app.lock'

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

USER_NAME = config['setting']['user_name']
VMRUN_PATH = config['setting']['vmrun_path'].replace('\\', '\\\\')
VMX_PATH = config['setting']['vmx_path'].replace('\\', '\\\\')
START_DELAY = int(config['setting']['start_delay'])
SERVER_URL = "http://127.0.0.1:2666"

def get_now():
    return f"[{datetime.now().strftime('%H:%M:%S')}] "

def get_active_window_hwnd():
    hwnd = win32gui.GetForegroundWindow()
    return hwnd

def is_admin():
    """檢查當前程式是否以管理員權限運行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def request_admin():
    """請求以管理員身份重新啟動程式"""
    if not is_admin():
        # 重新啟動程式，並要求管理員權限
        print("正在請求管理員權限...")
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()

def login():
    try:
        username = input(f"{get_now()}請輸入帳號：")
        password = input(f"{get_now()}請輸入密碼：")

        response = requests.post(f"{SERVER_URL}/login", json={"username": username, "password": password})
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success":
                client = Client(data['VMword'], VMRUN_PATH, VMX_PATH)
                client.login_VM()
                return data['clientId'], username
            else:
                print(f"{get_now()}密碼錯誤！")
        else:
            print(f"{get_now()}密碼錯誤！")

    except Exception as e:
        print(f"{get_now()}登入時發生錯誤, Error:{e}")
    return False

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
            print(f"{get_now()}正在啟動虛擬機...")
            subprocess.Popen([self.vmrun_path, "start", self.vmx_path])
            print(f"{get_now()}已發送虛擬機啟動請求！")
        except Exception as e:
            print(f"{get_now()}虛擬機啟動失敗：{e}")

    def auto_login_with_pyautogui(self):
        """使用 pyautogui 自動輸入密碼"""
        try:
            print(f"{get_now()}等待虛擬機登入介面加載...請不要做任何動作!!!")
            time.sleep(START_DELAY)

            print("自動輸入密碼中...")
            # pyautogui.hotkey('shift')
            hwnd = get_active_window_hwnd()
            for index in self.VMword:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
                pyautogui.typewrite(index)
            
            pyautogui.press("enter")
            print(f"{get_now()}密碼輸入成功！")
        except Exception as e:
            print(f"{get_now()}自動輸入密碼失敗：{e}")

async def listen_for_commands(clientId, account):
    try:
        WEBSOCKET_URL = f"ws://127.0.0.1:2666/websocket/{clientId}/{account}/{USER_NAME}"
        async with websockets.connect(WEBSOCKET_URL) as websocket:
            print(f"{get_now()}成功連上WebSocket, 裝置名稱:[{clientId}]")
            await asyncio.sleep(10)

            async def send_heartbeat():
                while True:
                    try:
                        count = manage.count_virtual_machine_processes()

                        if count == 0:
                            print(f"{get_now()}偵測虛擬機已經關閉, 程序即將退出..")
                            await asyncio.sleep(2)
                            sys.exit()

                        await websocket.send(f"{clientId}: 心跳包 ({count})")
                        print(f"{get_now()}傳送心跳包. [{clientId}]({count})")
                    except Exception as e:
                        print(f"{get_now()}傳送心跳包失敗: [{clientId}]{e}")
                        break
                    await asyncio.sleep(5)

            asyncio.create_task(send_heartbeat())

            while True:
                try:
                    # 等待伺服端的指令
                    command = await websocket.recv()
                    print(f"{get_now()}收到指令: {command}")

                    if command == "close_vmware_workstation":
                        manage.close_vmware_workstation()
                        await websocket.send(f"{clientId}: close_vmware_workstation 執行完畢")

                    if command == "restart_computer":
                        manage.restart_computer()
                        await websocket.send(f"{clientId}: restart_computer 執行完畢")

                    if command == "shutdown_computer":
                        manage.shutdown_computer()
                        await websocket.send(f"{clientId}: shutdown_computer 執行完畢")

                except websockets.ConnectionClosed:
                    print(f"{get_now()}WebSocket失去連線嘗試連接中...")
                    await asyncio.sleep(5)
                    await listen_for_commands(clientId, account)

    except Exception as e:
        print(f"{get_now()}Error connecting to WebSocket: {e}")

async def main():
    lock = FileLock(lockfile) # 檔案鎖
    try:
        lock.acquire(timeout=1)
    except Timeout:
        print("程序已在運行，禁止重複啟動。")
        await asyncio.sleep(3)
        return

    try:
        request_admin()
        clientId, account = login()
        if clientId:
            print(f"{get_now()}開始監聽..")
            await listen_for_commands(clientId, account)
        else:
            print(f"{get_now()}登入失敗, 即將退出..")
            await asyncio.sleep(3)
    finally:
        lock.release()

if __name__ == "__main__":
    asyncio.run(main())
