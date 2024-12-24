from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.responses import JSONResponse
from passlib.hash import bcrypt
import random
import string
from config.setting import db
import time
import json
import auth
from urllib.parse import unquote
from datetime import datetime
from pymongo import ReturnDocument

import requestClass

app = FastAPI()
# uvicorn main:app --host 127.0.0.1 --port 2666 --reload
# uvicorn main:app --host 192.168.0.106 --port 2666 --reload

connected_clients = {}

admin_permissions = ['admin', 'onwer']

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
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"創建虛擬機帳號時發生錯誤, {e}")

@app.post("/login")
async def login(request: requestClass.RegisterRequest):
    username = request.username
    account = request.account
    password = request.password

    collection = db['Accounts']
    user = collection.find_one({"account": account})
    if not user:
        raise HTTPException(status_code=401, detail="Account not found")
    
    if username not in connected_clients:
        raise HTTPException(status_code=401, detail="Service startup not detected")
    
    if bcrypt.verify(password, user["password"]):
        clientId = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
        return JSONResponse(content={
            "status": "success",
            "clientId": clientId,
            "VMword": user['VMword']
        })
    else:
        raise HTTPException(status_code=401, detail="Invalid password")
    
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
            raise HTTPException(status_code=404, detail=f"裝置ID無效 [{username}]")

        try:
            websocket = connected_clients[username]['websocket']
            await websocket.send_text(method)
            return JSONResponse(content={"status": "success", "message": f"{method} 已傳送至 {username}"})
        except Exception as e:
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
                await websocket.send_text("無效的消息格式，請發送正確的 JSON")
                continue

            if message['type'] == "heartbeat":
                heartbeat_process(username, message)

    except WebSocketDisconnect:
        print(f"用戶 {username} 已斷開連線.")
    except Exception as e:
        print(f"WebSocket 錯誤. 來自 {username}: {e}")
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