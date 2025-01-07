from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.responses import JSONResponse
from config.setting import db
import time
import json
import utils.auth as auth
from urllib.parse import unquote
from datetime import datetime

from utils import requestClass, log_event, get_client_ip, connected_clients

app = APIRouter()

@app.post("/list_connected")
@auth.login_required
async def list_connected(request: Request):
    try:
        user = auth.get_current_user(request)

        collection = db['Users']
        user = collection.find_one({"email": user.email})
        
        if user['role'] not in ['admin', 'owner']:
            raise HTTPException(status_code=400, detail="Insufficient account permissions")
        
        accountList = list(collection.find())

        clients_info = []
        for client_id, data in connected_clients.items():
            client_data = data.copy()
            client_data.pop('websocket', None)
            client_data['client_id'] = client_id
            
            account = next((account for account in accountList if account.get('nickname') == client_id), None)
            if account:
                client_data['role'] = account.get('role')
            else:
                client_data['role'] = 'Unknown'

            current_time = datetime.now().timestamp()
            connected_at = client_data.get('connected_at', 0)
            connection_duration = current_time - connected_at

            client_data['connection_duration'] = int(connection_duration)

            clients_info.append(client_data)

        result = {
            "code": 0,
            "message": clients_info
        }
        
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"取得線上裝置列表時發生錯誤, {e}")

@app.post("/oneclick_operation")
@auth.login_required
async def oneclick_operation(request: Request, body: requestClass.oneClickOperationClass):
    try:
        user = auth.get_current_user(request)

        collection = db['Users']
        user = collection.find_one({"email": user.email})

        if user['role'] not in ['admin', 'owner']:
            raise HTTPException(status_code=400, detail="Insufficient account permissions")
        
        operation = body.operation
        operation_command_list = ['close_vmware_workstation', 'restart_computer', 'shutdown_computer', 'close_chrome']
        
        if operation in operation_command_list:
            await oneclick_operation_process(request, user, operation)
            result = {
                'code': 0,
                'message': f"成功執行一鍵指令: {operation}"
            }
            return result
        else:
            log_event.insert_log("ERROR", user, None, "oneclick_operation", f"對全體成員進行未知指令，已被拒絕！", get_client_ip(request))
            raise HTTPException(status_code=404, detail=f"未知一鍵指令")

    except Exception as e:
        log_event.insert_log("ERROR", user, None, "oneclick_operation", f"對全體成員進行 {operation} 指令時發生錯誤！", get_client_ip(request))
        raise HTTPException(status_code=400, detail=f"管理員一鍵操作時發生錯誤, {e}")
    
async def oneclick_operation_process(request, user, operation):
    for key in connected_clients:
        websocket = connected_clients[key]['websocket']

        if not websocket:
            log_event.insert_log("WARN", user, None, "oneclick_operation", f"對全體成員進行 {operation} 時於用戶 {connected_clients[key]['username']} 連線錯誤！", get_client_ip(request))
            continue
        
        ws_msg = json.dumps({
            "type": "operation",
            "operate": operation
        })
        await websocket.send_text(ws_msg)
    log_event.insert_log("INFO", user, None, "oneclick_operation", f"對全體成員進行了 {operation} 指令。", get_client_ip(request))

@app.post("/oneclick_broadcast")
@auth.login_required
async def oneclick_broadcast(request: Request, body: requestClass.oneClickBroadcastClass):
    try:
        user = auth.get_current_user(request)

        collection = db['Users']
        user = collection.find_one({"email": user.email})

        if user['role'] not in ['admin', 'owner']:
            raise HTTPException(status_code=400, detail="Insufficient account permissions")
        
        content = body.content
        
        for key in connected_clients:
            websocket = connected_clients[key]['websocket']
            if not websocket:    
                print(f"{user['nickname']}對全體成員廣播時於用戶 {connected_clients[key]['username']} 連線錯誤！")
                log_event.insert_log("WARN", user, None, "oneclick_operation", f"對全體成員廣播時於用戶 {connected_clients[key]['username']} 連線錯誤！", get_client_ip(request))

            ws_msg = json.dumps({
                'type': 'broadcast',
                'msg': content
            })
            await websocket.send_text(ws_msg)

            result = {
                'code': 0,
                'message': f"成功執行一鍵廣播"
            }
        
        log_event.insert_log("INFO", user, None, "oneclick_operation", f"對全體成員廣播！", get_client_ip(request))

        return result

    except Exception as e:
        log_event.insert_log("ERROR", user, None, "oneclick_operation", f"對全體成員廣播時發生錯誤！", get_client_ip(request))
        raise HTTPException(status_code=400, detail=f"管理員一鍵操作時發生錯誤, {e}")
    
@app.post("/api")
@auth.login_required
async def api(request: Request, body: requestClass.ApiRequest):
    method = body.method
    content = body.content
    
    user = auth.get_current_user(request)

    collection = db['Users']
    user = collection.find_one({"email": user.email})

    if user['role'] not in ['admin', 'owner']:
        raise HTTPException(status_code=400, detail="Insufficient account permissions")

    command = {
        "close_vmware_workstation": "close_vmware_workstation",
        "restart_computer": "restart_computer",
        "shutdown_computer": "shutdown_computer",
        "close_chrome": "close_chrome"
    }
    
    if method == "message":
        username = content.get("username")

        if username not in connected_clients:
            raise HTTPException(status_code=404, detail=f"使用者ID無效 [{username}]")

        try:
            msg = content.get("msg")
            websocket = connected_clients[username]['websocket']

            ws_msg = json.dumps({
                'type': 'broadcast',
                'msg': msg
            })
            await websocket.send_text(ws_msg)
            return JSONResponse(content={"status": "success", "message": f"{msg} 已傳送至 {username}"})
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"傳送 {method} 指令失敗: {str(e)}")

    elif method in command:
        username = content.get("username")

        if username not in connected_clients:
            log_event.insert_log("ERROR", user, db['Users'].find_one({"nickname": username}), "operation_command", f"對[{username}]使用{method}指令失敗: 裝置ID無效", get_client_ip(request))
            raise HTTPException(status_code=404, detail=f"裝置ID無效 [{username}]")

        try:
            websocket = connected_clients[username]['websocket']
            ws_msg = json.dumps({
                "type": "operation",
                "operate": method
            })
            await websocket.send_text(ws_msg)
            log_event.insert_log("INFO", user, db['Users'].find_one({"nickname": username}), "operation_command", f"對[{username}]使用{method}指令成功", get_client_ip(request))
            return JSONResponse(content={"status": "success", "message": f"{method} 已傳送至 {username}"})
        except Exception as e:
            log_event.insert_log("ERROR", user, db['Users'].find_one({"nickname": username}), "operation_command", f"對[{username}]使用{method}指令失敗: {str(e)}", get_client_ip(request))
            raise HTTPException(status_code=500, detail=f"傳送 {method} 指令失敗: {str(e)}") 

    else:
        raise HTTPException(status_code=400, detail="無效Method.")
    
@app.post("/post_custom_command")
@auth.login_required
async def post_custom_command(request: Request, body: requestClass.customCommand):
    user = auth.get_current_user(request)

    collection = db['Users']
    user = collection.find_one({"email": user.email})

    if user['role'] not in ['admin', 'owner']:
        raise HTTPException(status_code=400, detail="Insufficient account permissions")
    
    username = body.selectedValue
    command = body.command

    if username not in connected_clients:
        raise HTTPException(status_code=404, detail=f"使用者ID無效 [{username}]")
    
    log_event.insert_log("INFO", user, db['Users'].find_one({"nickname": username}), "custom_operation_command", f"使用了調適功能", get_client_ip(request))
    try:
        websocket = connected_clients[username]['websocket']
        ws_msg = json.dumps({
            "type": "operation",
            "operate": "custom_command",
            "command": command
        })
        await websocket.send_text(ws_msg)
        return JSONResponse(content={"status": "success", "message": f"自訂指令已傳送至 {username}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"傳送自訂指令失敗: {str(e)}") 
      
@app.post("/call_update_client")
@auth.login_required
async def call_update_client(request: Request, body: requestClass.callUpdate):
    try:
        user = auth.get_current_user(request)

        collection = db['Users']
        user = collection.find_one({"email": user.email})

        if user['role'] not in ['admin', 'owner']:
            raise HTTPException(status_code=400, detail="Insufficient account permissions")
        
        username = body.username

        if username not in connected_clients:
            raise HTTPException(status_code=404, detail=f"使用者ID無效 [{username}]")

        websocket = connected_clients[username]['websocket']
        ws_msg = json.dumps({
            "type": "update"
        })
        await websocket.send_text(ws_msg)
        return JSONResponse(content={"status": "success", "message": f"更新客戶端指令已傳送"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新客戶端指令傳送失敗: {str(e)}") 

@app.websocket("/websocket/{username}/{version}")
async def websocket_endpoint(websocket: WebSocket, username: str, version: str):
    username = unquote(username)
    collection = db['Users']
    existing_user = collection.find_one({"nickname": username})

    if not existing_user:
        await websocket.accept()
        
        ws_msg = json.dumps({
            'type': 'usernotregistered'
        })
        await websocket.send_text(ws_msg)

        print(f"用戶 {username} 未註冊, 已拒絕連線.")
        await websocket.close()
        return

    # 接受 WebSocket 連接
    await websocket.accept()
    client_ip = websocket.client.host
    print(f"用戶 {username} 已連線. IP: {client_ip}")

    connected_clients[username] = {
        "websocket": websocket,
        "username": username,
        "connected_at": int(time.time()),
        "vmcount": 0,
        "ip": client_ip,
        "version": version
    }
    log_event.insert_log("INFO", existing_user, None, "websocket_connect", "已連線上伺服器主機", client_ip)

    try:
        while True:
            # 接收消息
            message = await websocket.receive_text()
            print(f"收到訊息來自 {username}: {message}")

            if not message.strip():
                print(f"收到空消息來自 {username}")
                continue

            try:
                message = json.loads(message)
            except json.JSONDecodeError:
                print(f"無效的 JSON 消息來自 {username}: {message}")
                continue

            if message['type'] == "heartbeat":
                await heartbeat_process(websocket, username, message)
            if message['type'] == "operate_result":
                print(message['operate_msg'])

    except WebSocketDisconnect:
        print(f"用戶 {username} 已斷開連線.")
        log_event.insert_log("INFO", existing_user, None, "websocket_disconnect", "已中斷伺服器主機連線", client_ip)
    except Exception as e:
        print(f"WebSocket 錯誤. 來自 {username}: {e}")
        log_event.insert_log("ERROR", existing_user, None, "websocket_connect_error", f"WebSocket 錯誤. {e}", client_ip)
    finally:
        # 移除斷開的連接
        try:
            if websocket:
                log_event.insert_log("WARN", existing_user, None, "websocket_closed", "WebSocket 已執行關閉", client_ip)
                await websocket.close()
        except Exception as e:
            pass
        finally:
            removed_client = connected_clients.pop(username, None)
            if removed_client:
                log_event.insert_log("DEBUG", existing_user, None, "client_removed", f"連線記錄已清理", client_ip)

async def heartbeat_process(websocket, username, message):
    try:
        vmcount = int(message['vmcount'])
        if connected_clients[username]['vmcount'] != vmcount:
            connected_clients[username]['vmcount'] = vmcount

        collection = db['Users']        
        collection.update_one(
            {"nickname": username},
            {"$inc": {"heartbeatCount": 1}}
        )

        ws_msg = json.dumps({
            "type": "pong"
        })
        await websocket.send_text(ws_msg)
    except Exception as e:
        print(f"Heartbeat 處理錯誤. 來自 {username}: {e}")