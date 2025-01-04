from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from config.setting import db
import time

from utils import requestClass, firebaseConfig

app = APIRouter()

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