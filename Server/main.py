from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import JSONResponse
from passlib.hash import bcrypt
import random
import string
from pydantic import BaseModel
from setting import db
import time

app = FastAPI()
# uvicorn main:app --host 127.0.0.1 --port 2666 --reload

connected_clients = {}

class RegisterRequest(BaseModel):
    username: str
    account: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class ApiRequest(BaseModel):
    method: str
    content: dict

@app.post("/register")
async def register(request: RegisterRequest):
    username = request.username
    account = request.account
    password = request.password

    collection = db['Users']

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
async def login(request: LoginRequest):
    username = request.username
    password = request.password

    collection = db['Users']
    user = collection.find_one({"account": username})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    if bcrypt.verify(password, user["password"]):
        clientId = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
        return JSONResponse(content={
            "status": "success",
            "clientId": clientId,
            "VMword": user['VMword']
        })
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
@app.get("/list_connected")
async def list_connected():
    clients_info = {}
    for client_id, data in connected_clients.items():
        client_data = data.copy()
        client_data.pop('websocket', None)
        clients_info[client_id] = client_data
    
    return JSONResponse(content={"connected_clients": clients_info})

@app.post("/api")
async def api(request: ApiRequest):
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

# WebSocket 端點
@app.websocket("/websocket/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    # 接受 WebSocket 連接
    await websocket.accept()
    print(f"用戶 {username} 已連線.")
    connected_clients[username] = {
        "websocket": websocket,
        "username": username,
        "connected_at": int(time.time())
    }

    try:
        while True:
            # 接收消息
            message = await websocket.receive_text()
            print(f"收到訊息來自 {username}: {message}")

            # # 回傳回聲消息
            # await websocket.send_text(f"Echo: {message}")
    except WebSocketDisconnect:
        print(f"用戶 {username} 已斷開連線.")
    except Exception as e:
        print(f"WebSocket 錯誤. 來自 {username}: {e}")
    finally:
        # 移除斷開的連接
        connected_clients.pop(username, None)
