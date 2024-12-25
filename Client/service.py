import sys
import threading
import time
import configparser
import os
import json
import asyncio
import websockets
from datetime import datetime
from urllib.parse import quote
import tkinter as tk

import manage

SERVICE_VERSION = "v1.0.1"
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

    async def run(self):
        while self.running:
            try:
                async with websockets.connect(f"{WEBSOCKET_URL}/websocket/{quote(USER_NAME)}/{SERVICE_VERSION}") as websocket:
                    write_log("已連接到 WebSocket 服務器")
                    await self.handle_connection(websocket)
            except Exception as e:
                write_log(f"WebSocket 連接失敗: {e}")
                await asyncio.sleep(5)  # 重試間隔

    async def handle_connection(self, websocket):
        async def send_heartbeat():
            while True:
                await asyncio.sleep(self.heartbeat_interval)
                heartbeat_message = {
                        "type": "heartbeat",
                        "user": USER_NAME,
                        "timestamp": int(time.time()),
                        "vmcount": manage.count_virtual_machine_processes()
                }
                await websocket.send(json.dumps(heartbeat_message))
                # write_log("心跳包已發送")

        heartbeat_task = asyncio.create_task(send_heartbeat())
        try:
            while True:
                server_message = await websocket.recv()
                await self.on_message(websocket, server_message)
                
        except websockets.exceptions.ConnectionClosedError:
            write_log("連線已被伺服器關閉")
        except Exception as e:
            write_log(f"WebSocket 錯誤: {e}")
        finally:
            heartbeat_task.cancel()
            write_log("與 WebSocket 伺服器的連線已結束")

    async def on_message(self, websocket, message):
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
        
        elif message == "usernotregistered":
            write_log("收到 usernotregistered 訊息，停止服務並退出程序。")
            self.running = False
            await websocket.close()
            write_log("WebSocket 連線已關閉，程序即將結束。")

        else:
            await self.display_broadcast_message(message)

    async def display_broadcast_message(self, message):
        def show_popup():
            popup = tk.Tk()
            popup.overrideredirect(True)

            label = tk.Label(popup, text=message, font=("Arial", 16), bg="black", fg="yellow")
            label.pack(expand=True, fill="both")

            popup.update()

            label_width = label.winfo_reqwidth()
            label_height = label.winfo_reqheight()

            screen_width = popup.winfo_screenwidth()

            window_width = max(label_width + 20, 100)
            window_height = max(label_height + 20, 50)

            x = (screen_width - window_width) // 2
            y = 20

            popup.geometry(f"{window_width}x{window_height}+{x}+{y}")
            popup.update()
            print(f"Popup geometry set to: {window_width}x{window_height}+{x}+{y}")

            popup.attributes("-topmost", True)
            popup.configure(bg="black")
            popup.attributes("-alpha", 0.8)

            popup.after(2000, popup.destroy)
            popup.mainloop()

        threading.Thread(target=show_popup).start()

        await asyncio.sleep(2)

async def main():
    client = WebSocketClient()
    await client.run()

if __name__ == "__main__":
    asyncio.run(main())
