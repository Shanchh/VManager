from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.responses import JSONResponse
from passlib.hash import bcrypt
import random
import string
from config.setting import db
import time
import json
import auth

import requestClass

app = FastAPI()
# uvicorn main:app --host 127.0.0.1 --port 2666 --reload

connected_clients = {}

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
        "role": role
    }

    r = collection.insert_one(userData)
    
    result = {
        "code": 0,
        "message": "User registered successfully"
    }

    return result

@app.post("/get_my_profile")
async def get_my_profile(request: requestClass.GetProfileRequest):
    email = request.email
    
    collection = db['Users']
    userData = collection.find_one({"email": email})
    userData.pop("_id", None)

    return {"message": userData}

@app.post("/register")
async def register(request: requestClass.RegisterRequest):
    username = request.username
    account = request.account
    password = request.password

    collection = db['Accounts']

    existing_user = collection.find_one({"account": account})
    if existing_user:
        raise HTTPException(status_code=400, detail="Account already exists")

    VMword = ''.join(random.choices(string.ascii_letters + string.digits, k=48))

    new_user = {
        "username": username,
        "account": account,
        "password": password,
        "VMword": VMword
    }
    
    collection.insert_one(new_user)

    return {"message": "Account registered successfully", "username": username, "account": account, "VMword": VMword}

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
async def list_connected():
    clients_info = {}
    for client_id, data in connected_clients.items():
        client_data = data.copy()
        client_data.pop('websocket', None)
        clients_info[client_id] = client_data
    
    return JSONResponse(content={"connected_clients": clients_info})

@app.post("/api")
async def api(request: requestClass.ApiRequest):
    method = request.method
    content = request.content
    
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

@app.websocket("/websocket/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    collection = db['Accounts']
    existing_user = collection.find_one({"username": username})

    if not existing_user:
        await websocket.accept()
        await websocket.send_text("usernotregistered")
        print(f"用戶 {username} 未註冊, 已拒絕連線.")
        await websocket.close()
        return

    # 接受 WebSocket 連接
    await websocket.accept()
    print(f"用戶 {username} 已連線.")
    connected_clients[username] = {
        "websocket": websocket,
        "username": username,
        "connected_at": int(time.time()),
        "vmcount": 0
    }

    try:
        while True:
            # 接收消息
            message = await websocket.receive_text()
            print(f"收到訊息來自 {username}: {message}")

            message = json.loads(message)
            if message['type'] == "heartbeat":
                heartbeat_process(username, message)

            # # 回傳回聲消息
            # await websocket.send_text(f"Echo: {message}")
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
    except Exception as e:
        print(f"Heartbeat 處理錯誤. 來自 {username}: {e}")