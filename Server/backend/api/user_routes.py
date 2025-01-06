from fastapi import APIRouter, HTTPException, Request
import random
import string
from config.setting import db
import time
import utils.auth as auth
from pymongo import ReturnDocument

from utils import requestClass, log_event, get_client_ip

app = APIRouter()

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

@app.post("/get_my_20_activities")
@auth.login_required
async def get_my_20_activities(request: Request):
    try:
        user = auth.get_current_user(request)

        user = db['Users'].find_one({"email": user.email})

        collection = db['Logs']
        logs = list(collection.find({"requester.id": str(user['_id']), "level": "INFO"}).sort("timestamp", -1).limit(9))

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