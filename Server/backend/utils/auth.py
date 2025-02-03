from fastapi import Request, Depends, HTTPException
from functools import wraps
from .firebaseConfig import db, auth
from firebase_admin._user_mgt import UserRecord

def get_token_with_headers(request: Request) -> str:
    """獲取Token"""
    try:
        authorization = request.headers.get("Authorization")
        if authorization:
            return authorization.split("Bearer ")[1]
        return ""
    except:
        return ""

def get_current_user(request: Request) -> UserRecord:
    """獲取當前User"""
    try:
        token = get_token_with_headers(request)
        result = auth.verify_id_token(token, clock_skew_seconds=60)
        return auth.get_user(result["user_id"])
    except Exception:
        return None

def login_required(func):
    """登入裝飾器"""
    @wraps(func)
    async def wrapper(*args, request: Request, **kwargs):
        user = get_current_user(request)
        if user is None:
            raise HTTPException(status_code=403, detail="please login!")
        return await func(*args, request=request, **kwargs)

    return wrapper

def auth_check():
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            raise HTTPException(status_code=404, detail="404")
        return wrapper

    return decorator