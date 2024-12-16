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
import psutil
import subprocess
import os
import sys
import ctypes

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
                client = Client(data['VMword'], data['vmrun_path'], data['vmx_path'])
                client.login_VM()
                return data['clientId']
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
            time.sleep(5)

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

async def listen_for_commands(clientId):
    try:
        WEBSOCKET_URL = f"ws://127.0.0.1:2666/websocket/{clientId}"
        async with websockets.connect(WEBSOCKET_URL) as websocket:
            print(f"{get_now()}成功連上WebSocket, 裝置名稱:[{clientId}]")
            time.sleep(10)

            async def send_heartbeat():
                while True:
                    try:
                        count = count_virtual_machine_processes()

                        if count == 0:
                            print(f"{get_now()}偵測虛擬機已經關閉, 程序即將退出..")
                            time.sleep(2)
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
                        close_vmware_workstation()
                        await websocket.send(f"{clientId}: close_vmware_workstation執行完畢")

                except websockets.ConnectionClosed:
                    print(f"{get_now()}WebSocket失去連線嘗試連接中...")
                    await asyncio.sleep(5)
                    await listen_for_commands(clientId)

    except Exception as e:
        print(f"{get_now()}Error connecting to WebSocket: {e}")

def count_virtual_machine_processes():
    # 定義虛擬機進程名稱
    vm_process_names = ["vmware-vmx.exe", "VirtualBoxVM", "vmwp.exe"]

    # 遍歷系統中的所有進程
    vm_count = 0
    for proc in psutil.process_iter(attrs=["pid", "name"]):
        try:
            # 獲取進程名稱
            process_name = proc.info["name"]
            if process_name in vm_process_names:
                vm_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return vm_count

def list_virtual_machine_processes():
    # 定義虛擬機相關進程名稱
    vm_process_names = ["vmware-vmx.exe", "VirtualBoxVM", "vmwp.exe"]  # 根據需要添加更多進程名稱

    # 用於存儲虛擬機進程信息的列表
    vm_processes = []

    for proc in psutil.process_iter(attrs=["pid", "name", "cpu_percent", "memory_info"]):
        try:
            # 獲取進程名稱
            process_name = proc.info["name"]
            if process_name in vm_process_names:
                # 收集進程的詳細信息
                vm_processes.append({
                    "進程名稱": process_name,
                    "PID": proc.info["pid"],
                    "CPU 使用率 (%)": proc.info["cpu_percent"],
                    "記憶體佔用 (MB)": proc.info["memory_info"].rss / 1024 / 1024
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return vm_processes

def kill_process_by_name(process_name):
    """
    強制關閉所有指定名稱的進程
    :param process_name: 進程名稱（字符串，例如 'vmware-vmx.exe'）
    """
    try:
        # 遍歷系統中的所有進程
        for proc in psutil.process_iter(attrs=["pid", "name"]):
            if proc.info["name"] == process_name:
                print(f"正在關閉進程: {proc.info['name']} (PID: {proc.info['pid']})")
                proc.kill()  # 強制關閉進程
                print(f"進程 {proc.info['name']} (PID: {proc.info['pid']}) 已關閉。")
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
        print(f"無法關閉進程: {e}")

def close_vmware_workstation():
    try:
        # 使用 taskkill 關閉 VMware Workstation 主程序
        subprocess.run(["taskkill", "/F", "/IM", "vmware.exe"], check=True)
        print("VMware Workstation 主程序已關閉。")

        # 使用 taskkill 關閉所有 VMware 虛擬機進程
        subprocess.run(["taskkill", "/F", "/IM", "vmware-vmx.exe"], check=True)
        print("所有 VMware 虛擬機進程已關閉。")
    except subprocess.CalledProcessError as e:
        print(f"關閉 VMware 進程時發生錯誤: {e}")
    except Exception as ex:
        print(f"發生未知錯誤: {ex}")

def restart_computer():
    try:
        # Windows 系統
        if os.name == 'nt':
            os.system("shutdown /r /t 0")  # 立即重啟
        # macOS 或 Linux 系統
        else:
            os.system("sudo reboot")
        print("重啟命令已執行。")
    except Exception as e:
        print(f"執行重啟時發生錯誤: {e}")

def shutdown_computer():
    try:
        # Windows 系統
        if os.name == 'nt':
            os.system("shutdown /s /t 0")  # 立即關機
        # macOS 或 Linux 系統
        else:
            os.system("sudo shutdown now")
        print("關機命令已執行。")
    except Exception as e:
        print(f"執行關機時發生錯誤: {e}")

async def main():
    request_admin()

    clientId = login()
    if clientId:
        print(f"{get_now()}開始監聽..")
        await listen_for_commands(clientId)
    else:
        print(f"{get_now()}登入失敗, 即將退出..")
        time.sleep(3)

if __name__ == "__main__":
    asyncio.run(main())
