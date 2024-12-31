from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from passlib.hash import bcrypt
import random
import string
from config.setting import db
import time
import json
import auth as auth
from urllib.parse import unquote
from datetime import datetime
from pymongo import ReturnDocument
import uvicorn

import requestClass
import log_event
import firebaseConfig

app = FastAPI()
# uvicorn main:app --host 127.0.0.1 --port 2666 --reload
# uvicorn main:app --host 192.168.0.106 --port 2666 --reload

app.mount("/static", StaticFiles(directory="build/static"), name="static")

@app.get("/")
async def serve_root():
    return FileResponse("build/index.html")

# 提供其他路径的文件，支持 React 的路由
@app.get("/{path:path}")
async def serve_other_paths(path: str):
    return FileResponse("build/index.html")

connected_clients = {}

admin_permissions = ['admin', 'onwer']

def get_client_ip(request: Request) -> str:
    client_ip = request.headers.get("x-forwarded-for")
    if client_ip:
        return client_ip.split(",")[0].strip()
    return request.client.host

@app.post("/create_user")
async def create_user(request: requestClass.CreateUserRequest):
    email = request.email
    nickname = request.nickname
    role = 'user'

    collection = db['Users']

    existing_user = collection.find_one({"email": email})
    if existing_user:
        raise HTTPException(status_code=400, detail="信箱已註冊!")
    
    userData = {
        "email": email,
        "nickname": nickname,
        "role": role,
        "createAt": int(time.time()),
        "VMisCreate": False,
        "heartbeatCount": 0
    }

    r = collection.insert_one(userData)
    
    result = {
        "code": 0,
        "message": "User registered successfully"
    }

    return result

@app.post("/get_my_profile")
@auth.login_required
async def get_my_profile(request: Request, body: requestClass.GetProfileRequest):
    email = body.email
    
    collection = db['Users']
    userData = collection.find_one({"email": email})
    userData.pop("_id", None)

    return {"message": userData}

@app.post("/get_my_data")
@auth.login_required
async def get_my_data(request: Request):
    try:
        user = auth.get_current_user(request)

        collection = db['Users']
        user = collection.find_one({"email": user.email})
        user['_id'] = str(user['_id'])

        result = {
            "code": 0,
            "message": user
        }
        
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"取得帳號資料時發生錯誤, {e}")

@app.post("/get_all_account_data")
@auth.login_required
async def get_all_account_data(request: Request):
    try:
        user = auth.get_current_user(request)

        collection = db['Users']
        user = collection.find_one({"email": user.email})
        
        if user['role'] not in ['admin', 'owner']:
            raise HTTPException(status_code=400, detail="Insufficient account permissions")
        
        accountList = list(collection.find())

        for account in accountList:
            account['_id'] = str(account['_id'])

        result = {
            "code": 0,
            "message": accountList
        }
        
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"取得帳號列表時發生錯誤, {e}")
    
@app.post("/get_my_20_activities")
@auth.login_required
async def get_my_20_activities(request: Request):
    try:
        user = auth.get_current_user(request)

        user = db['Users'].find_one({"email": user.email})

        collection = db['Logs']
        logs = list(collection.find({"requester.id": str(user['_id'])}).sort("timestamp", -1).limit(9))

        for log in logs:
            log['_id'] = str(log['_id'])

        result = {
            "code": 0,
            "message": logs
        }

        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"取得動態時發生錯誤, {e}")
    
@app.post("/get_server_logs")
@auth.login_required
async def get_server_info_logs(request: Request, body: requestClass.getServerLogs):
    try:
        user = auth.get_current_user(request)

        user = db['Users'].find_one({"email": user.email})

        if user['role'] not in ['owner']:
            raise HTTPException(status_code=400, detail="Insufficient account permissions")
        
        logLevel = body.level

        collection = db['Logs']
        logs = list(collection.find({"level": logLevel}).sort("timestamp", -1).limit(100))

        for log in logs:
            log['_id'] = str(log['_id'])

        result = {
            "code": 0,
            "message": logs
        }

        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"取得日誌時發生錯誤, {e}")

@app.post("/register_vmware")
@auth.login_required
async def register_vmware(request: Request):
    try:
        user = auth.get_current_user(request)

        collection = db['Users']
        user = collection.find_one_and_update(
            {"email": user.email},
            {"$set": {"VMisCreate": True}},
            return_document=ReturnDocument.AFTER
        )

        if not user:
            raise HTTPException(status_code=404, detail="找不到指令用戶")

        collection = db['Accounts']
        VMword = ''.join(random.choices(string.ascii_letters + string.digits, k=48))
        insert_data = {
            "nickname": user['nickname'],
            "email": user['email'],
            "VMword": VMword,
            "createAt": int(time.time())
        }
        r = collection.insert_one(insert_data)

        result = {
            "code": 0,
            "message": {
                "VMword": VMword,
                "inserted_id": str(r.inserted_id)
            }
        }

        log_event.insert_log("INFO", user, None, "register_vmware", "註冊虛擬機", get_client_ip(request))
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"創建虛擬機帳號時發生錯誤, {e}")

@app.post("/login")
async def login(request: requestClass.RegisterRequest):
    try:
        email = request.email
        password = request.password

        user = firebaseConfig.auth.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=401, detail="帳號不存在")

        id_token = password
        decoded_token = firebaseConfig.auth.verify_id_token(id_token)
        uid = decoded_token.get("uid")

        user = firebaseConfig.auth.get_user(uid)
        if user.disabled:
            raise HTTPException(status_code=403, detail="帳號被禁用")

        # 从数据库中获取用户信息
        collection = db["Accounts"]
        user_data = collection.find_one({"email": email})
        if not user_data:
            raise HTTPException(status_code=404, detail="帳號不存在")

        return JSONResponse(content={
            "status": "success",
            "VMword": user_data["VMword"]
        })

        raise HTTPException(status_code=401, detail="帳號被禁用")
    except firebaseConfig.auth.AuthError as e:
        raise HTTPException(status_code=401, detail="帳號認證失敗")
    except Exception as e:
        raise HTTPException(status_code=500, detail="伺服器錯誤")
    
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

        await websocket.send_text(operation)
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
            await websocket.send_text(content)

            result = {
                'code': 0,
                'message': f"成功執行一鍵廣播"
            }
        
        log_event.insert_log("INFO", user, None, "oneclick_operation", f"對全體成員廣播！", get_client_ip(request))

        return result

    except Exception as e:
        log_event.insert_log("ERROR", user, None, "oneclick_operation", f"對全體成員廣播時發生錯誤！", get_client_ip(request))
        raise HTTPException(status_code=400, detail=f"管理員一鍵操作時發生錯誤, {e}")
    
@app.post("/delete_account")
@auth.login_required
async def delete_account(request: Request, body: requestClass.deleteAccountClass):
    try:
        user = auth.get_current_user(request)

        collection = db['Users']
        user = collection.find_one({"email": user.email})

        if user['role'] not in ['admin', 'owner']:
            raise HTTPException(status_code=400, detail="Insufficient account permissions")
        
        account = body.data

        firebase_account = firebaseConfig.auth.get_user_by_email(account['email'])
        firebaseConfig.auth.delete_user(firebase_account.uid)

        collection.delete_one({"email": account['email']})

        collection = db['Accounts']
        collection.delete_one({"email": account['email']})

        result = {
            'code': 0,
            'message': f"成功刪除帳號"
        }
        
        log_event.insert_log("INFO", user, account, "delete_account", f"刪除了 {account['nickname']} 的帳號！", get_client_ip(request))

        return result

    except Exception as e:
        log_event.insert_log("ERROR", user, None, "oneclick_operation", f"刪除 {account['nickname']} 帳號時發生錯誤！", get_client_ip(request))
        raise HTTPException(status_code=400, detail=f"刪除帳號時發生錯誤！, {e}")

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
            await websocket.send_text(msg)
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
            await websocket.send_text(method)
            log_event.insert_log("INFO", user, db['Users'].find_one({"nickname": username}), "operation_command", f"對[{username}]使用{method}指令成功", get_client_ip(request))
            return JSONResponse(content={"status": "success", "message": f"{method} 已傳送至 {username}"})
        except Exception as e:
            log_event.insert_log("ERROR", user, db['Users'].find_one({"nickname": username}), "operation_command", f"對[{username}]使用{method}指令失敗: {str(e)}", get_client_ip(request))
            raise HTTPException(status_code=500, detail=f"傳送 {method} 指令失敗: {str(e)}") 

    else:
        raise HTTPException(status_code=400, detail="無效Method.")

@app.websocket("/websocket/{username}/{version}")
async def websocket_endpoint(websocket: WebSocket, username: str, version: str):
    username = unquote(username)
    collection = db['Users']
    existing_user = collection.find_one({"nickname": username})

    if not existing_user:
        await websocket.accept()
        await websocket.send_text("usernotregistered")
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
                heartbeat_process(username, message)

    except WebSocketDisconnect:
        print(f"用戶 {username} 已斷開連線.")
        log_event.insert_log("INFO", existing_user, None, "websocket_disconnect", "已中斷伺服器主機連線", client_ip)
    except Exception as e:
        print(f"WebSocket 錯誤. 來自 {username}: {e}")
        log_event.insert_log("ERROR", existing_user, None, "websocket_connect_error", "已中斷伺服器主機連線", client_ip)
    finally:
        # 移除斷開的連接
        if websocket:
            await websocket.close()
            log_event.insert_log("WARN", existing_user, None, "websocket_close", "Websocket執行關閉", client_ip)
        connected_clients.pop(username, None)

def heartbeat_process(username, message):
    try:
        vmcount = int(message['vmcount'])
        if connected_clients[username]['vmcount'] != vmcount:
            connected_clients[username]['vmcount'] = vmcount

        collection = db['Users']        
        collection.update_one(
            {"nickname": username},
            {"$inc": {"heartbeatCount": 1}}
        )
    except Exception as e:
        print(f"Heartbeat 處理錯誤. 來自 {username}: {e}")

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=2626, reload=True)