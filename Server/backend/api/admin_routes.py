from fastapi import APIRouter, HTTPException, Request
from config.setting import db
import utils.auth as auth

from utils import requestClass, log_event, firebaseConfig, get_client_ip

app = APIRouter()

admin_permissions = ['admin', 'onwer']

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