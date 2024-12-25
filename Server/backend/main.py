from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.responses import JSONResponse
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

import requestClass
import log_event
import firebaseConfig

app = FastAPI()
# uvicorn main:app --host 127.0.0.1 --port 2666 --reload
# uvicorn main:app --host 192.168.0.106 --port 2666 --reload

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

@app.get("/get_my_data")
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

@app.get("/get_all_account_data")
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
    
@app.get("/get_my_20_activities")
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
    
@app.get("/list_connected")
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
        "shutdown_computer": "shutdown_computer"
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