from fastapi import HTTPException
import string
from config.setting import db
from typing import Optional
from datetime import datetime

log_debug_switch = True


def insert_log(level: string, requester_data: dict, recipient_data: Optional[dict], action: string, message: string, ipAddress: string):
    try:
        if not log_debug_switch:
            print("日誌功能關閉中，未紀錄日誌")
            return

        if recipient_data:
            recipient_data = {
                "id": str(recipient_data['_id']),
                "email": recipient_data['email'],
                "nickname": recipient_data['nickname']
            }

        log_data = {
            "timestamp": datetime.now(),
            "level": level,
            "action": action,
            "requester": {
                "id": str(requester_data['_id']),
                "email": requester_data['email'],
                "nickname": requester_data['nickname']
            },
            "recipient": recipient_data if recipient_data else None,
            "details": {
                "message": message
            },
            "ipAddress": ipAddress
        }

        collection = db['Logs']
        collection.insert_one(log_data)

    except Exception as e:
        raise HTTPException(status_code=404, detail=f"寫入Log時發生錯誤, 發生於({requester_data['email']}) {e}")