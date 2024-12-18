import configparser
import os
from datetime import datetime
import time
import pyperclip
import requests
from passlib.hash import bcrypt

config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
config = configparser.ConfigParser()
config.read(config_path, encoding='utf-8')

USER_NAME = config['setting']['user_name']
SERVER_URL = config['setting']['server_ip']

def print_welcome():
    print("┍" + "━" * 26 + "┑")
    print("│" + " " * 5 + "VManager註冊系統"+ " " * 5 + "│")
    print("┕" + "━" * 26 + "┙")

def get_time_now():
    return f"[{datetime.now().strftime('%H:%M:%S')}] "

def main():
    while True:
        account = input(f"{get_time_now()}請輸入欲註冊帳號：")
        password = input(f"{get_time_now()}請輸入欲註冊密碼：")
        password_confirm = input(f"{get_time_now()}確認密碼：")

        if account == "" or password == "" or password_confirm == "":
            print(f"{get_time_now()}帳號密碼不可為空！\n━")
            continue

        if len(password) < 9:
            print(f"{get_time_now()}密碼不可小於8位數！\n━")
            continue

        if password != password_confirm:
            print(f"{get_time_now()}密碼與確認密碼不一致，請重新輸入..\n━")
            continue

        response = requests.post(f"{SERVER_URL}/register", json={"username": USER_NAME, "account": account, "password": bcrypt.hash(password)})
        data = response.json()
        VMword = data.get("VMword")

        pyperclip.copy(VMword)
        print(f"{get_time_now()}註冊成功！使用者名稱：{USER_NAME}, 帳號：{account}, 虛擬機密碼：{VMword}")
        print(f"將於60秒後關閉程式...")
        time.sleep(60)
        break  

if __name__ == "__main__":
    print_welcome()
    main()