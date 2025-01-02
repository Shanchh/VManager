import sys
import time
import configparser
import os
import json
import asyncio
import websockets
from datetime import datetime
from urllib.parse import quote

import manage

SERVICE_VERSION = "v1.0.3"
SERVICE_DISPLAY_NAME = f"VManager監測 {SERVICE_VERSION}"

def get_executable_dir():
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

log_path = os.path.join(get_executable_dir(), 'log.yml')
config_path = os.path.join(get_executable_dir(), 'config.ini')
config = configparser.ConfigParser()
config.read(config_path, encoding='utf-8')

USER_NAME = config['setting']['user_name']
WEBSOCKET_URL = config['setting']['websocket_url']

def get_now():
    return f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "

def write_log(msg):
    with open(log_path, 'a', encoding="utf-8") as f:
        f.write(f"{get_now()}{msg}\n")

class WebSocketClient:
    def __init__(self):
        self.running = True
        self.heartbeat_interval = 5
        self.retryCount = 0
        self.heartbeat_running = False
        self.last_message_time = None
        self.timeout_interval = 8

    async def run(self):
        while self.running:
            try:
                async with websockets.connect(f"{WEBSOCKET_URL}/websocket/{quote(USER_NAME)}/{SERVICE_VERSION}") as websocket:
                    self.retryCount = 0
                    write_log("已連接到 WebSocket 服務器")
                    self.last_message_time = time.time()
                    await self.handle_connection(websocket)
            except Exception as e:
                write_log(f"WebSocket 連接失敗: {e}")
                self.retryCount += 1
                if self.retryCount >= 6 and manage.count_virtual_machine_processes() > 0:
                    # write_log(f"重試次數: {self.retryCount}, 強制關閉虛擬機。") 
                    manage.close_vmware_workstation()
                await asyncio.sleep(5)  # 重試間隔

    async def handle_connection(self, websocket):
        async def send_heartbeat():
            self.heartbeat_running = True
            try:
                while True:
                    await asyncio.sleep(self.heartbeat_interval)
                    heartbeat_message = {
                        "type": "heartbeat",
                        "user": USER_NAME,
                        "timestamp": int(time.time()),
                        "vmcount": manage.count_virtual_machine_processes()
                    }
                    await websocket.send(json.dumps(heartbeat_message))
            finally:
                self.heartbeat_running = False

        async def monitor_timeout():
            try:
                while True:
                    await asyncio.sleep(1)
                    if self.last_message_time and (time.time() - self.last_message_time > self.timeout_interval):
                        write_log("超過 8 秒未收到訊息，將重新連接 WebSocket")
                        await websocket.close()
                        break
            except asyncio.CancelledError:
                pass

        if not self.heartbeat_running:
            heartbeat_task = asyncio.create_task(send_heartbeat())
        timeout_task = asyncio.create_task(monitor_timeout())
        
        try:
            while True:
                server_message = await websocket.recv()
                self.last_message_time = time.time()  # 更新最後接收時間
                await self.on_message(websocket, server_message)
        except websockets.exceptions.ConnectionClosedError:
            write_log("連線已被伺服器關閉")
        except Exception as e:
            write_log(f"WebSocket 錯誤: {e}")
        finally:
            heartbeat_task.cancel()
            timeout_task.cancel()
            try:
                await heartbeat_task
                await timeout_task
            except asyncio.CancelledError:
                pass
            write_log("與 WebSocket 伺服器的連線已結束")

    async def on_message(self, websocket, message):
        if message == "pong":
            self.last_message_time = time.time()
            self.retryCount = 0
            return

        write_log(f"來自伺服器的訊息: {message}")
        if message == "close_vmware_workstation":
            manage.close_vmware_workstation()
            await websocket.send(f"{USER_NAME}: close_vmware_workstation 執行完畢")

        elif message == "restart_computer":
            manage.restart_computer()
            await websocket.send(f"{USER_NAME}: restart_computer 執行完畢")

        elif message == "shutdown_computer":
            manage.shutdown_computer()
            await websocket.send(f"{USER_NAME}: shutdown_computer 執行完畢")

        elif message == "close_chrome":
            manage.close_chrome()
            await websocket.send(f"{USER_NAME}: close_chrome 執行完畢")
        
        elif message == "usernotregistered":
            write_log("收到 usernotregistered 訊息，停止服務並退出程序。")
            self.running = False
            await websocket.close()
            write_log("WebSocket 連線已關閉，程序即將結束。")

        else:
            write_log(f"非指令訊息 {message}")

async def main():
    client = WebSocketClient()
    await client.run()

if __name__ == "__main__":
    asyncio.run(main())
