import sys
import win32serviceutil
import win32service
import win32event
import time
import configparser
import os
from datetime import datetime
import threading
import websocket

config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log.yml')
config = configparser.ConfigParser()
config.read(config_path, encoding='utf-8')

USER_NAME = config['setting']['user_name']
VMRUN_PATH = config['setting']['vmrun_path'].replace('\\', '\\\\')
VMX_PATH = config['setting']['vmx_path'].replace('\\', '\\\\')
START_DELAY = int(config['setting']['start_delay'])
SERVER_URL = config['setting']['server_ip']
WEBSOCKET_URL = config['setting']['websocket_url']

def get_now():
    return f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "

def write_log(msg):
    with open(log_path, 'a', encoding="utf-8") as f:
        f.write(f"{get_now()}{msg}\n")

class WebSocketClient:
    def __init__(self):
        self.running = True
        self.lock = threading.Lock()
        self.ws = None
        self.heartbeat_interval = 5
        self.connect()

    def connect(self):
        """建立 WebSocket 連接並設置回調函數"""
        try:
            write_log("正在嘗試連接 WebSocket...")
            ws_url = f"{WEBSOCKET_URL}/websocket/{USER_NAME}"
            self.ws = websocket.WebSocketApp(
                ws_url,
                on_open=self.on_open,
                on_message=self.on_message,
                on_close=self.on_close,
                on_error=self.on_error
            )
            threading.Thread(target=self.ws.run_forever, daemon=True).start()
        except Exception as e:
            write_log(f"連接WebSocket失敗: {e}")
            self.reconnect()

    def on_open(self, ws):
        write_log("WebSocket 連接成功，啟動心跳包...")
        self.running = True
        threading.Thread(target=self.send_heartbeat, daemon=True).start()

    def on_message(self, ws, message):
        write_log(f"收到消息: {message}")

    def on_close(self, ws, close_status_code, close_msg):
        write_log("WebSocket 連接已關閉，5 秒後重新連接...")
        self.running = False
        self.reconnect()

    def on_error(self, ws, error):
        write_log(f"WebSocket 錯誤: {error}")
        self.reconnect()

    def send_heartbeat(self):
        """定期發送心跳包，確保連線保持活躍"""
        while self.running:
            try:
                if self.ws and self.ws.sock and self.ws.sock.connected:
                    heartbeat_msg = f'{{"type": "heartbeat", "user": "{USER_NAME}", "timestamp": "{datetime.now().isoformat()}"}}'
                    with self.lock:
                        self.ws.send(heartbeat_msg)
                    # write_log("發送心跳包")
                else:
                    write_log("WebSocket 未連接，跳過發送心跳包")
            except Exception as e:
                write_log(f"發送心跳包時發生錯誤: {e}")
            time.sleep(self.heartbeat_interval)

    def reconnect(self):
        """5 秒後重新連接"""
        if not self.running:
            time.sleep(5)
            self.connect()


class MyService(win32serviceutil.ServiceFramework):
    _svc_name_ = "北匯電腦管理"
    _svc_display_name_ = "VManager監測"
    _svc_start_type_ = win32service.SERVICE_AUTO_START

    def __init__(self, args):
        super().__init__(args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.running = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.running = False

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)

        ws_client = WebSocketClient()

        while self.running:
            # 模擬服務工作邏輯，定時輸出日誌
            # write_log("服務執行中")
            time.sleep(5)

if __name__ == "__main__":
    if "install" in sys.argv:
        win32serviceutil.HandleCommandLine(MyService)
        print("服務已安裝。正在啟動服務...")
        try:
            win32serviceutil.StartService(MyService._svc_name_)
            print("服務啟動成功.")
        except Exception as e:
            print(f"啟動服務失敗: {e}")
    else:
        win32serviceutil.HandleCommandLine(MyService)
