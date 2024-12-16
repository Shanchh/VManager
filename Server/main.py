from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import JSONResponse
from passlib.hash import bcrypt
import random
import string
from pydantic import BaseModel
from setting import db

app = FastAPI()
# uvicorn main:app --host 127.0.0.1 --port 2666 --reload

connected_clients = {}

class LoginRequest(BaseModel):
    username: str
    password: str

class ApiRequest(BaseModel):
    method: str
    content: dict

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
            "VMword": user['VMword'],
            "vmrun_path": user['vmrun_path'],
            "vmx_path": user['vmx_path']
        })
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
@app.get("/list_connected")
async def list_connected():
    client_ids = list(connected_clients.keys())
    return JSONResponse(content={"client_ids": client_ids})

@app.post("/api")
async def api(request: ApiRequest):
    method = request.method
    content = request.content
    
    if method == "close_vmware_workstation":
        client_id = content.get("clientId")
        
        if client_id not in connected_clients:
            raise HTTPException(status_code=404, detail=f"裝置ID無效 [{client_id}]")
        
        try:
            websocket = connected_clients[client_id]
            await websocket.send_text("close_vmware_workstation")
            return JSONResponse(content={"status": "success", "message": f"close_vmware_workstation 已傳送至 {client_id}"})
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"傳送 close_vmware_workstation 指令失敗: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail="無效Method.")

# WebSocket 端點
@app.websocket("/websocket/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    # 接受 WebSocket 連接
    await websocket.accept()
    print(f"Client {client_id} connected.")
    connected_clients[client_id] = websocket

    try:
        while True:
            # 接收消息
            message = await websocket.receive_text()
            print(f"Received from {client_id}: {message}")

            # # 回傳回聲消息
            # await websocket.send_text(f"Echo: {message}")
    except WebSocketDisconnect:
        print(f"Client {client_id} disconnected.")
    except Exception as e:
        print(f"WebSocket error for {client_id}: {e}")
    finally:
        # 移除斷開的連接
        connected_clients.pop(client_id, None)
