from fastapi import APIRouter, HTTPException, Request
from config.setting import db
import utils.auth as auth
from datetime import datetime, timedelta
from bson import ObjectId

from utils import requestClass, log_event, firebaseConfig, get_client_ip

app = APIRouter()

admin_permissions = ['admin', 'owner']

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
    
@app.post("/get_user_log_data")
@auth.login_required
async def get_user_log_data(request: Request, body: requestClass.getUserLogs):
    try:
        user = auth.get_current_user(request)

        user = db['Users'].find_one({"email": user.email})

        if user['role'] not in ['owner']:
            raise HTTPException(status_code=400, detail="Insufficient account permissions")
        
        date = body.date
        userId = body.userId
        logType = body.logType

        start_date = datetime(date.year, date.month, date.day)
        end_date = start_date + timedelta(days=1)

        match_condition = {
            "timestamp": {"$gte": start_date, "$lt": end_date}
        }

        if userId != "all":
            match_condition["requester.id"] = userId
        if logType != "all":
            match_condition["level"] = logType

        collection = db['Logs']
        log_data = list(collection.find(match_condition))

        for log in log_data:
            log['_id'] = str(log['_id'])

        result = {
            "code": 0,
            "message": "logs",
            "data": log_data
        }

        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"取得日誌時發生錯誤, {e}")
    
@app.post("/get_user_log_counts_data")
@auth.login_required
async def get_user_log_counts_data(request: Request, body: requestClass.getLogCount):
    try:
        user = auth.get_current_user(request)
        user = db['Users'].find_one({"email": user.email})

        if not user or user['role'] not in ['owner']:
            raise HTTPException(status_code=400, detail="Insufficient account permissions")
        
        date = body.date
        userId = body.userId
        
        start_date = date - timedelta(days=10)
        end_date = date
        
        match_condition = {
            "timestamp": {"$gte": start_date, "$lte": end_date},
            "level": {"$in": ["INFO", "WARN", "ERROR", "DEBUG"]}
        }

        if userId != "all":
            match_condition["requester.id"] = userId

        collection = db['Logs']
        pipeline = [
            {"$match": match_condition},
            {
                "$group": {
                    "_id": {
                        "level": "$level",
                        "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}}
                    },
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id.date": 1}}
        ]

        logs = list(collection.aggregate(pipeline))
        
        result_data = [
            {
                "category": log["_id"]["level"],
                "value": log["count"],
                "time": log["_id"]["date"]
            }
            for log in logs
        ]

        result = {
            "code": 0,
            "message": "logs",
            "data": result_data
        }

        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"取得日誌數量時發生錯誤, {e}")
    
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
    
@app.post("/get_average_daily_count")
@auth.login_required
async def get_average_daily_count(request: Request):
    try:
        user = auth.get_current_user(request)

        user = db['Users'].find_one({"email": user.email})

        if user['role'] not in admin_permissions:
            raise HTTPException(status_code=400, detail="Insufficient account permissions")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=10)

        pipeline = [
            {
                "$match": {
                    "timestamp": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                    "average_online_count": {"$avg": "$online_count"}
                }
            },
            {
                "$sort": {"_id": 1}
            }
        ]

        result = list(db['OnlineStats'].aggregate(pipeline))

        daily_averages = [
            {
                "date": item["_id"],
                "average_online_count": round(item["average_online_count"], 2)
            }
            for item in result
        ]

        all_dates = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(10)]
        final_result = [
            {
                "date": date,
                "average_online_count": next(
                    (item["average_online_count"] for item in daily_averages if item["date"] == date), 0
                )
            }
            for date in all_dates
        ]

        result = {
            "code": 0,
            "message": final_result
        }

        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"取得每日平均上限裝置數時發生錯誤, {e}")
    
@app.post("/modify_user_role")
@auth.login_required
async def modify_user_role(request: Request, body: requestClass.modifyRoleClass):
    try:
        user = auth.get_current_user(request)
        current_user = db['Users'].find_one({"email": user.email})

        if current_user['role'] not in admin_permissions:
            raise HTTPException(status_code=400, detail="Insufficient account permissions")

        role = body.role
        objId = body.objId

        target_user = db['Users'].find_one({"_id": ObjectId(objId)})
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")

        update_result = db['Users'].update_one(
            {"_id": ObjectId(objId)},
            {"$set": {"role": role}}
        )

        if update_result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Failed to update user role")

        result = {
            "code": 0,
            "message": f"User role updated successfully to {role}"
        }

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"修改用戶身分組時發生錯誤, {e}")