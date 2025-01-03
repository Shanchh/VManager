import subprocess
import psutil
import subprocess
import os

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
    if count_virtual_machine_processes() >= 1:
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

def close_chrome():
    try:
        result = subprocess.run(['tasklist'], stdout=subprocess.PIPE, text=True)
        if 'chrome.exe' in result.stdout:
            os.system("taskkill /F /IM chrome.exe")
            print("Google Chrome 已關閉")
        else:
            print("未偵測到Google Chrome進程")
    except Exception as e:
        print(f"關閉Google Chrome進程發生錯誤: {e}")