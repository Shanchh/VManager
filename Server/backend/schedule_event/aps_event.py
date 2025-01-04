from datetime import datetime, timedelta
from config.setting import db

from utils import connected_clients

collection = db["OnlineStats"]

def record_online_users():
    try:
        current_time = datetime.now()
        online_count = len(connected_clients)
        
        existing_record = collection.find_one({
            "timestamp": {
                "$gte": current_time - timedelta(seconds=10),
                "$lte": current_time + timedelta(seconds=10)
            }
        })
        
        if not existing_record:
            collection.insert_one({
                "timestamp": current_time,
                "online_count": online_count
            })
            print(f"已記錄在線人數: {online_count} 時間: {current_time}")
    except Exception as e:
        print(f"記錄在線人數時發生錯誤: {e}")
